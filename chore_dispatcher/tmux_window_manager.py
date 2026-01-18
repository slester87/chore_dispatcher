"""
TMUX Window Manager

Core system for managing TMUX sessions and windows for chore workflow.
"""

import subprocess
import json
import os
import shutil
import platform
import time
import logging
from typing import Optional, List, Dict

logger = logging.getLogger("chore_dispatcher.tmux")


class TMUXWindowManager:
    """Manages TMUX sessions and windows for chore workflow integration."""
    
    def __init__(self, session_name: str = "chores"):
        self.session_name = session_name
    
    def _get_platform_tmux_paths(self) -> List[str]:
        """Get platform-specific tmux binary paths."""
        system = platform.system().lower()
        
        if system == 'darwin':  # macOS
            return [
                '/opt/homebrew/bin/tmux',
                '/usr/bin/tmux',
                '/usr/local/bin/tmux'
            ]
        elif system == 'linux':
            return [
                '/usr/bin/tmux',
                '/usr/local/bin/tmux'
            ]
        else:
            return ['/usr/bin/tmux']
    
    def _get_tmux_binary(self) -> str:
        """Get the tmux binary path."""
        tmux_paths = self._get_platform_tmux_paths()
        
        for path in tmux_paths:
            if os.path.exists(path):
                return path
        
        # Fallback to PATH
        tmux_path = shutil.which('tmux')
        if tmux_path:
            return tmux_path
        
        raise RuntimeError("tmux binary not found")
    
    def _detect_current_session(self) -> Optional[str]:
        """Detect current tmux session name if running inside tmux."""
        try:
            tmux_binary = self._get_tmux_binary()
            result = subprocess.run([
                tmux_binary, 'display-message', '-p', '#S'
            ], capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0:
                session_name = result.stdout.strip()
                logger.debug(f"Detected current tmux session: {session_name}")
                return session_name
            else:
                logger.debug("Not running inside tmux session")
                return None
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, RuntimeError) as e:
            logger.debug(f"Failed to detect tmux session: {e}")
            return None
    
    def _validate_session_exists(self, session_name: str) -> bool:
        """Validate that a tmux session exists."""
        try:
            tmux_binary = self._get_tmux_binary()
            result = subprocess.run([
                tmux_binary, 'has-session', '-t', session_name
            ], capture_output=True, text=True, timeout=3)
            
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, RuntimeError):
            return False
    
    def _is_valid_session_name(self, session_name: str) -> bool:
        """Validate session name format for tmux compatibility."""
        if not session_name or not isinstance(session_name, str):
            return False
        
        # tmux session names cannot contain: / * spaces and some other special chars
        invalid_chars = ['/', '*', ' ', '\t', '\n', '\r']
        return not any(char in session_name for char in invalid_chars)
    
    def _get_target_session(self, session_id: Optional[str] = None) -> str:
        """Get target session with priority handling: explicit → current → fallback.
        
        Args:
            session_id: Optional explicit session name to use
            
        Returns:
            str: Valid session name (never None)
            
        Raises:
            RuntimeError: If explicit session_id is provided but invalid
        """
        # Priority 1: Explicit session_id provided
        if session_id is not None:
            logger.debug(f"Using explicit session_id: {session_id}")
            # Validate session name format first
            if not self._is_valid_session_name(session_id):
                logger.error(f"Invalid session name format: {session_id}")
                raise RuntimeError(f"Invalid session name '{session_id}': contains invalid characters")
            
            # Create session if it doesn't exist
            if not self._validate_session_exists(session_id):
                logger.info(f"Creating new tmux session: {session_id}")
                try:
                    tmux_binary = self._get_tmux_binary()
                    result = subprocess.run([
                        tmux_binary, 'new-session', '-d', '-s', session_id
                    ], capture_output=True, text=True, timeout=5)
                    
                    if result.returncode != 0:
                        logger.error(f"Failed to create session {session_id}: {result.stderr}")
                        raise RuntimeError(f"Failed to create session '{session_id}': {result.stderr}")
                    
                    logger.debug(f"Session created successfully: {session_id}")
                    # Brief delay for session creation
                    time.sleep(0.5)
                    
                    # Verify session was created
                    if not self._validate_session_exists(session_id):
                        logger.error(f"Session creation verification failed: {session_id}")
                        raise RuntimeError(f"Session creation verification failed for '{session_id}'")
                        
                except subprocess.TimeoutExpired:
                    logger.error(f"Session creation timed out: {session_id}")
                    raise RuntimeError(f"Session creation timed out for '{session_id}'")
            else:
                logger.debug(f"Using existing session: {session_id}")
            
            return session_id
        
        # Priority 2: Current tmux session
        current_session = self._detect_current_session()
        if current_session and self._validate_session_exists(current_session):
            logger.info(f"Using current tmux session: {current_session}")
            return current_session
        
        # Priority 3: Fallback to default session
        fallback_session = self.session_name
        logger.info(f"Using fallback session: {fallback_session}")
        
        # Create session if it doesn't exist
        if not self._validate_session_exists(fallback_session):
            logger.info(f"Creating fallback session: {fallback_session}")
            try:
                tmux_binary = self._get_tmux_binary()
                result = subprocess.run([
                    tmux_binary, 'new-session', '-d', '-s', fallback_session
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode != 0:
                    logger.error(f"Failed to create fallback session: {result.stderr}")
                    raise RuntimeError(f"Failed to create fallback session '{fallback_session}': {result.stderr}")
                
                logger.debug(f"Fallback session created successfully: {fallback_session}")
                # Brief delay for session creation
                time.sleep(0.5)
                
                # Verify session was created
                if not self._validate_session_exists(fallback_session):
                    logger.error(f"Fallback session creation verification failed: {fallback_session}")
                    raise RuntimeError(f"Session creation verification failed for '{fallback_session}'")
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Fallback session creation timed out: {fallback_session}")
                raise RuntimeError(f"Session creation timed out for '{fallback_session}'")
        
    def has_existing_session(self) -> bool:
        """Check if TMUX session exists."""
        return self._validate_session_exists(self.session_name)
    
    def attach_or_create_session(self, session_id: Optional[str] = None) -> Dict[str, str]:
        """Attach to existing session or create new one with priority logic."""
        try:
            target_session = self._get_target_session(session_id)
            detected_current = self._detect_current_session()
            
            if session_id:
                selection_reason = f"explicit_session_id: {session_id}"
            elif detected_current:
                selection_reason = f"current_session: {detected_current}"
            else:
                selection_reason = f"fallback: {self.session_name}"
            
            return {
                "session_name": target_session,
                "attach_command": f"tmux attach-session -t {target_session}",
                "selection_reason": selection_reason,
                "detected_current_session": detected_current or "none",
                "success": True
            }
        except Exception as e:
            return {
                "session_name": "",
                "attach_command": "",
                "selection_reason": "error",
                "detected_current_session": "error", 
                "success": False,
                "error": str(e)
            }
        """Attach to existing session or create new one with priority logic.
        
        Returns:
            Dict with session info and attach command
        """
        try:
            # Get target session using priority logic
            target_session = self._get_target_session(session_id)
            
            # Collect session detection info
            detected_current = self._detect_current_session()
            
            # Determine selection reason
            if session_id:
                selection_reason = f"explicit_session_id: {session_id}"
            elif detected_current:
                selection_reason = f"current_session: {detected_current}"
            else:
                selection_reason = f"fallback: {self.session_name}"
            
            return {
                "session_name": target_session,
                "attach_command": f"tmux attach-session -t {target_session}",
                "selection_reason": selection_reason,
                "detected_current_session": detected_current or "none",
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Session attachment failed: {e}")
            return {
                "session_name": "",
                "attach_command": "",
                "selection_reason": "error",
                "detected_current_session": "error",
                "success": False,
                "error": str(e)
            }
        """Check if TMUX session exists."""
        return self._validate_session_exists(self.session_name)
    
    def create_session(self) -> bool:
        """Create new TMUX session."""
        try:
            tmux_binary = self._get_tmux_binary()
            subprocess.run([tmux_binary, 'new-session', '-d', '-s', self.session_name], 
                          check=True)
            return True
        except (subprocess.CalledProcessError, RuntimeError):
            return False
    
    def create_chore_window(self, chore_id: int, chore_name: str, session_id: Optional[str] = None) -> bool:
        """Create dedicated window for chore with session context."""
        try:
            # Use session attachment logic
            session_info = self.attach_or_create_session(session_id)
            if not session_info['success']:
                logger.error(f"Session attachment failed: {session_info.get('error', 'Unknown error')}")
                return False
            
            target_session = session_info['session_name']
            window_name = f"chore_{chore_id}"
            tmux_binary = self._get_tmux_binary()
            
            # Create window
            subprocess.run([tmux_binary, 'new-window', '-t', target_session, 
                          '-n', window_name], check=True)
            
            # Set window title to chore name (truncated)
            title = chore_name[:30] + "..." if len(chore_name) > 30 else chore_name
            subprocess.run([tmux_binary, 'rename-window', '-t', f"{target_session}:{window_name}", 
                          title], check=True)
            
            # Post-creation validation
            time.sleep(0.5)  # Brief delay for window creation
            if not self._validate_window_created(chore_id, target_session):
                logger.error(f"Window validation failed: {window_name}")
                return False
            
            logger.info(f"Chore window created: {window_name} in session {target_session}")
            return True
            
        except (subprocess.CalledProcessError, RuntimeError) as e:
            logger.error(f"Window creation failed: {e}")
            return False
    
    def _validate_window_created(self, chore_id: int, session_name: str) -> bool:
        """Validate that the tmux window was actually created."""
        try:
            tmux_binary = self._get_tmux_binary()
            result = subprocess.run([
                tmux_binary, 'list-windows', '-t', session_name, '-F', '#{window_name}'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                return False
            
            # Check if our chore window is in the list
            window_name = f"chore_{chore_id}"
            windows = result.stdout.strip().split('\n')
            return window_name in windows
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            return False
    
    def get_attach_command(self, session_id: Optional[str] = None) -> str:
        """Get command to attach to session."""
        session_info = self.attach_or_create_session(session_id)
        return session_info.get('attach_command', f'tmux attach-session -t {self.session_name}')
    
    def get_session_info(self, session_id: Optional[str] = None) -> Dict[str, str]:
        """Get comprehensive session information."""
        return self.attach_or_create_session(session_id)
    
    def remove_chore_window(self, chore_id: int) -> bool:
        """Remove chore window when complete."""
        try:
            window_name = f"chore_{chore_id}"
            tmux_binary = self._get_tmux_binary()
            subprocess.run([tmux_binary, 'kill-window', '-t', f"{self.session_name}:{window_name}"], 
                          check=True)
            return True
        except (subprocess.CalledProcessError, RuntimeError):
            return False
    
    def list_chore_windows(self) -> List[Dict]:
        """List all active chore windows."""
        if not self.has_existing_session():
            return []
        
        try:
            tmux_binary = self._get_tmux_binary()
            result = subprocess.run([tmux_binary, 'list-windows', '-t', self.session_name, 
                                   '-F', '#{window_name}'], 
                                  capture_output=True, text=True, check=True)
            
            windows = []
            for line in result.stdout.strip().split('\n'):
                if line.startswith('chore_'):
                    chore_id = int(line.replace('chore_', ''))
                    windows.append({'chore_id': chore_id, 'window_name': line})
            
            return windows
        except (subprocess.CalledProcessError, RuntimeError, ValueError):
            return []


def integrate_with_chore_lifecycle():
    """Integration point for chore lifecycle events."""
    manager = TMUXWindowManager()
    
    # Example usage:
    # manager.create_chore_window(12345, "Implement user authentication")
    # manager.remove_chore_window(12345)
    
    return manager


if __name__ == "__main__":
    # Test the implementation
    manager = TMUXWindowManager()
    print(f"TMUX available: {manager.has_existing_session() or manager.create_session()}")
    print(f"Active windows: {manager.list_chore_windows()}")
