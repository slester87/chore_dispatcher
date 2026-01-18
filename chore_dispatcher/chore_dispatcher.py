#!/usr/bin/env python3
"""
TMUX Chore Worker Dispatcher

Manages dedicated TMUX windows for chore workers in isolated session.
"""

import subprocess
import logging
import re
from typing import Optional, List, Dict
from tmux_window_manager import TMUXWindowManager
from chore import Chore

logger = logging.getLogger(__name__)

class ChoreDispatcher:
    """Manages TMUX session and windows for chore workers."""
    
    def __init__(self, session_name: str = "chore-dispatcher"):
        self.session_name = session_name
        self.tmux_manager = TMUXWindowManager()
        self.kiro_cli_path = "/Applications/Kiro\\ CLI.app/Contents/MacOS/kiro-cli"
        self.trusted_tools = "@chore-dispatcher,read,write,web_fetch,web_search,grep,glob,shell,code"
        
    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')[:30]  # Limit length
        
    def _get_window_name(self, chore: Chore) -> str:
        """Generate window name for chore."""
        name_slug = self._slugify(chore.name)
        return f"chore-{chore.id}-{name_slug}"
        
    def ensure_dispatcher_session(self) -> bool:
        """Ensure chore-dispatcher session exists."""
        try:
            # Check if session exists
            result = subprocess.run(
                ["tmux", "has-session", "-t", self.session_name],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Session {self.session_name} already exists")
                return True
                
            # Create new session
            subprocess.run(
                ["tmux", "new-session", "-d", "-s", self.session_name],
                check=True
            )
            logger.info(f"Created session {self.session_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to ensure session: {e}")
            return False
            
    def create_worker_window(self, chore: Chore) -> bool:
        """Create dedicated window for chore worker."""
        if not self.ensure_dispatcher_session():
            return False
            
        window_name = self._get_window_name(chore)
        
        try:
            # Create window with kiro-cli command
            command = f"{self.kiro_cli_path} chat --trust-tools {self.trusted_tools}"
            
            subprocess.run([
                "tmux", "new-window", 
                "-t", self.session_name,
                "-n", window_name,
                "-c", "/Users/skippo/Development/KIRO",
                command
            ], check=True)
            
            logger.info(f"Created worker window: {window_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create worker window: {e}")
            return False
            
    def cleanup_worker_window(self, chore_id: int) -> bool:
        """Remove window for completed chore."""
        try:
            # Find window by chore ID pattern
            result = subprocess.run([
                "tmux", "list-windows", "-t", self.session_name, "-F", "#{window_name}"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"Session {self.session_name} not found")
                return False
                
            for window_name in result.stdout.strip().split('\n'):
                if window_name.startswith(f"chore-{chore_id}-"):
                    subprocess.run([
                        "tmux", "kill-window", "-t", f"{self.session_name}:{window_name}"
                    ], check=True)
                    logger.info(f"Cleaned up window: {window_name}")
                    return True
                    
            logger.warning(f"No window found for chore {chore_id}")
            return False
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to cleanup window: {e}")
            return False
            
    def list_active_windows(self) -> List[Dict[str, str]]:
        """List all chore windows in dispatcher session."""
        try:
            result = subprocess.run([
                "tmux", "list-windows", "-t", self.session_name, 
                "-F", "#{window_name}:#{window_active}"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return []
                
            windows = []
            for line in result.stdout.strip().split('\n'):
                if ':' in line and line.startswith('chore-'):
                    name, active = line.split(':', 1)
                    windows.append({
                        'name': name,
                        'active': active == '1'
                    })
                    
            return windows
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list windows: {e}")
            return []
            
    def attach_to_session(self) -> bool:
        """Attach to dispatcher session."""
        try:
            subprocess.run(["tmux", "attach-session", "-t", self.session_name], check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to attach to session: {e}")
            return False
