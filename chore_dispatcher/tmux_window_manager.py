"""
TMUX Window Manager

Core system for managing TMUX sessions and windows for chore workflow.
"""

import subprocess
import json
from typing import Optional, List, Dict


class TMUXWindowManager:
    """Manages TMUX sessions and windows for chore workflow integration."""
    
    def __init__(self, session_name: str = "chores"):
        self.session_name = session_name
    
    def has_existing_session(self) -> bool:
        """Check if TMUX session exists."""
        try:
            result = subprocess.run(['tmux', 'list-sessions'], 
                                  capture_output=True, text=True, check=False)
            return self.session_name in result.stdout
        except FileNotFoundError:
            return False
    
    def create_session(self) -> bool:
        """Create new TMUX session."""
        try:
            subprocess.run(['tmux', 'new-session', '-d', '-s', self.session_name], 
                          check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def create_chore_window(self, chore_id: int, chore_name: str) -> bool:
        """Create dedicated window for chore."""
        if not self.has_existing_session():
            if not self.create_session():
                return False
        
        try:
            window_name = f"chore_{chore_id}"
            subprocess.run(['tmux', 'new-window', '-t', self.session_name, 
                          '-n', window_name], check=True)
            
            # Set window title to chore name (truncated)
            title = chore_name[:30] + "..." if len(chore_name) > 30 else chore_name
            subprocess.run(['tmux', 'rename-window', '-t', f"{self.session_name}:{window_name}", 
                          title], check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def remove_chore_window(self, chore_id: int) -> bool:
        """Remove chore window when complete."""
        try:
            window_name = f"chore_{chore_id}"
            subprocess.run(['tmux', 'kill-window', '-t', f"{self.session_name}:{window_name}"], 
                          check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def list_chore_windows(self) -> List[Dict]:
        """List all active chore windows."""
        if not self.has_existing_session():
            return []
        
        try:
            result = subprocess.run(['tmux', 'list-windows', '-t', self.session_name, 
                                   '-F', '#{window_name}'], 
                                  capture_output=True, text=True, check=True)
            
            windows = []
            for line in result.stdout.strip().split('\n'):
                if line.startswith('chore_'):
                    chore_id = int(line.replace('chore_', ''))
                    windows.append({'chore_id': chore_id, 'window_name': line})
            
            return windows
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
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
