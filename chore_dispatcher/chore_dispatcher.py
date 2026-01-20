#!/usr/bin/env python3
"""
TMUX Chore Worker Dispatcher

Manages dedicated TMUX windows for chore workers in isolated session.
"""

import subprocess
import logging
import re
from typing import Optional, List, Dict, Any
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
        """Create dedicated window for chore worker with context."""
        if not self.ensure_dispatcher_session():
            return False
            
        window_name = self._get_window_name(chore)
        
        try:
            # Generate worker context
            context = self._generate_chore_context(chore, "worker")
            command = self._build_env_command(context, f"{self.kiro_cli_path} chat --trust-tools {self.trusted_tools}")
            
            subprocess.run([
                "tmux", "new-window", 
                "-t", self.session_name,
                "-n", window_name,
                "-c", "/Users/skippo/Development/KIRO",
                command
            ], check=True)
            
            # Set pane title for worker
            subprocess.run([
                "tmux", "select-pane", "-t", f"{self.session_name}:{window_name}",
                "-T", "worker"
            ], check=True)
            
            logger.info(f"Created worker window with context: {window_name}")
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
            
    def update_chore_context(self, chore: Chore) -> bool:
        """Update context in existing panes when chore status changes."""
        window_name = self._get_window_name(chore)
        
        try:
            # Get pane list for window
            result = subprocess.run([
                "tmux", "list-panes", "-t", f"{self.session_name}:{window_name}", "-F", "#{pane_index}"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return False
                
            pane_indices = result.stdout.strip().split('\n')
            
            # Update each pane with new context
            for i, pane_index in enumerate(pane_indices):
                role = "worker" if i == 0 else "reviewer"
                context = self._generate_chore_context(chore, role)
                
                # Set environment variables in pane
                for key, value in context.items():
                    subprocess.run([
                        "tmux", "send-keys", "-t", f"{self.session_name}:{window_name}.{pane_index}",
                        f"export {key}='{value}'", "Enter"
                    ], check=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to update context: {e}")
            return False
            
    def rename_chore_window(self, chore: Chore, old_window_name: str = None) -> bool:
        """Rename window based on current chore status."""
        if not old_window_name:
            old_window_name = self._get_window_name(chore)
        
        new_window_name = self._get_window_name_with_status(chore)
        
        try:
            subprocess.run([
                "tmux", "rename-window", 
                "-t", f"{self.session_name}:{old_window_name}",
                new_window_name
            ], check=True)
            logger.info(f"Renamed window: {old_window_name} -> {new_window_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to rename window: {e}")
            return False

    def _get_window_name_with_status(self, chore: Chore) -> str:
        """Generate window name including status."""
        name_slug = self._slugify(chore.name)
        status_slug = chore.status.value.lower().replace('_', '-')
        return f"chore-{chore.id}-{name_slug}-{status_slug}"

    def list_detailed_windows(self) -> List[Dict[str, Any]]:
        """List windows with detailed chore information."""
        try:
            result = subprocess.run([
                "tmux", "list-windows", "-t", self.session_name,
                "-F", "#{window_name}:#{window_active}:#{window_panes}"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return []
            
            windows = []
            for line in result.stdout.strip().split('\n'):
                if ':' in line and line.startswith('chore-'):
                    parts = line.split(':')
                    if len(parts) >= 3:
                        name, active, panes = parts[0], parts[1] == '1', int(parts[2])
                        
                        # Extract chore info from window name
                        chore_info = self._parse_window_name(name)
                        pane_roles = self._get_pane_roles(name)
                        
                        windows.append({
                            'name': name,
                            'active': active,
                            'panes': panes,
                            'chore_id': chore_info.get('id'),
                            'status': chore_info.get('status'),
                            'pane_roles': pane_roles
                        })
            return windows
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list windows: {e}")
            return []

    def _parse_window_name(self, window_name: str) -> Dict[str, Any]:
        """Parse chore information from window name."""
        # Parse: chore-{ID}-{name-slug}-{status}
        parts = window_name.split('-')
        if len(parts) >= 4 and parts[0] == 'chore':
            try:
                return {
                    'id': int(parts[1]),
                    'status': parts[-1].replace('-', '_').upper()
                }
            except ValueError:
                pass
        return {}

    def attach_to_chore_window(self, chore_id: int, pane_index: int = None) -> bool:
        """Attach to specific chore window and optionally focus pane."""
        windows = self.list_detailed_windows()
        target_window = None
        
        for window in windows:
            if window.get('chore_id') == chore_id:
                target_window = window['name']
                break
        
        if not target_window:
            logger.error(f"No window found for chore {chore_id}")
            return False
        
        try:
            # Select window
            subprocess.run([
                "tmux", "select-window", "-t", f"{self.session_name}:{target_window}"
            ], check=True)
            
            # Focus specific pane if requested
            if pane_index is not None:
                subprocess.run([
                    "tmux", "select-pane", "-t", f"{self.session_name}:{target_window}.{pane_index}"
                ], check=True)
            
            logger.info(f"Selected window {target_window}" + (f", pane {pane_index}" if pane_index is not None else ""))
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to attach to window: {e}")
            return False
            
    def create_reviewer_pane(self, chore: Chore) -> bool:
        """Create reviewer pane with context."""
        window_name = self._get_window_name(chore)
        
        try:
            # Check if worker window exists
            if not self._window_exists(window_name):
                logger.warning(f"No worker window found for chore {chore.id}, creating window first")
                self.create_worker_window(chore)
                
            # Generate reviewer context
            context = self._generate_chore_context(chore, "reviewer")
            command = self._build_env_command(context, f"{self.kiro_cli_path} chat --trust-tools {self.trusted_tools}")
            
            subprocess.run([
                "tmux", "split-window", 
                "-t", f"{self.session_name}:{window_name}",
                "-h",  # Horizontal split
                command
            ], check=True)
            
            # Set pane title for reviewer (pane index 1)
            subprocess.run([
                "tmux", "select-pane", "-t", f"{self.session_name}:{window_name}.1",
                "-T", "reviewer"
            ], check=True)
            
            logger.info(f"Created reviewer pane with context: {window_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create reviewer pane: {e}")
            return False
            
    def cleanup_reviewer_pane(self, chore: Chore) -> bool:
        """Remove reviewer pane while preserving worker pane."""
        window_name = self._get_window_name(chore)
        
        try:
            # Check if window exists
            if not self._window_exists(window_name):
                return True  # Already cleaned up
                
            # Kill pane 1 (reviewer pane) if it exists
            subprocess.run([
                "tmux", "kill-pane", "-t", f"{self.session_name}:{window_name}.1"
            ], check=True)
            
            logger.info(f"Cleaned up reviewer pane: {window_name}")
            return True
            
        except subprocess.CalledProcessError:
            # Pane doesn't exist or already cleaned up
            return True

    def _get_pane_roles(self, window_name: str) -> List[str]:
        """Get role information for panes in a window."""
        try:
            result = subprocess.run([
                "tmux", "list-panes", "-t", f"{self.session_name}:{window_name}",
                "-F", "#{pane_index}"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return []
            
            pane_count = len(result.stdout.strip().split('\n'))
            
            # Determine roles based on pane count and chore status
            if pane_count == 1:
                return ["worker"]
            elif pane_count == 2:
                return ["worker", "reviewer"]
            else:
                # Fallback for unexpected pane counts
                return [f"pane-{i}" for i in range(pane_count)]
                
        except subprocess.CalledProcessError:
            return []

    def _window_exists(self, window_name: str) -> bool:
        """Check if window exists in session."""
        try:
            result = subprocess.run([
                "tmux", "list-windows", "-t", self.session_name, "-F", "#{window_name}"
            ], capture_output=True, text=True)
            
            return window_name in result.stdout.strip().split('\n')
        except subprocess.CalledProcessError:
            return False
            
    def _generate_chore_context(self, chore: Chore, role: str = "worker") -> Dict[str, str]:
        """Generate environment variables for chore context."""
        return {
            'CHORE_ID': str(chore.id),
            'CHORE_NAME': chore.name,
            'CHORE_DESCRIPTION': chore.description,
            'CHORE_STATUS': chore.status.value,
            'CHORE_ROLE': role.upper()
        }

    def _build_env_command(self, env_vars: Dict[str, str], base_command: str) -> str:
        """Build command with environment variables."""
        env_prefix = ' '.join([f'{k}="{v}"' for k, v in env_vars.items()])
        return f'{env_prefix} {base_command}'
