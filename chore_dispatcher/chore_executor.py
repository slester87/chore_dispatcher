"""
Chore Executor

Integrates instruction parsing with TMUX window management for automatic execution.
"""

from typing import Optional, Dict, Any
from chore_instruction_parser import ChoreInstructionParser
from tmux_window_manager import TMUXWindowManager
import logging

logger = logging.getLogger("chore_dispatcher.executor")


class ChoreExecutor:
    """Executes chores automatically in dedicated TMUX windows."""
    
    def __init__(self, session_name: str = "chores"):
        self.parser = ChoreInstructionParser()
        self.tmux = TMUXWindowManager(session_name)
    
    def execute_chore_in_window(self, chore_id: int, chore_name: str, 
                               chore_description: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute chore automatically in dedicated TMUX window."""
        try:
            # Parse chore instruction
            instruction = self.parser.get_command_for_chore(chore_name, chore_description)
            
            logger.info(f"Executing chore {chore_id}: {chore_name}")
            logger.debug(f"Command: {instruction.command}")
            logger.debug(f"Working dir: {instruction.working_dir}")
            
            # Create window with automatic command execution
            success = self.tmux.create_chore_window_with_command(
                chore_id=chore_id,
                chore_name=chore_name,
                command=instruction.command,
                working_dir=instruction.working_dir,
                session_id=session_id
            )
            
            if success:
                session_info = self.tmux.get_session_info(session_id)
                return {
                    "success": True,
                    "chore_id": chore_id,
                    "chore_name": chore_name,
                    "command": instruction.command,
                    "working_dir": instruction.working_dir,
                    "session_name": session_info["session_name"],
                    "window_name": f"chore_{chore_id}",
                    "attach_command": session_info["attach_command"],
                    "message": f"Chore {chore_id} executing in TMUX window"
                }
            else:
                return {
                    "success": False,
                    "chore_id": chore_id,
                    "error": "Failed to create TMUX window with command",
                    "command": instruction.command
                }
                
        except Exception as e:
            logger.error(f"Chore execution failed: {e}")
            return {
                "success": False,
                "chore_id": chore_id,
                "error": str(e)
            }
    
    def execute_chore_from_repository(self, chore_id: int, session_id: Optional[str] = None, 
                                    data_path: Optional[str] = None) -> Dict[str, Any]:
        """Execute chore directly from repository data."""
        from chore_repository import ChoreRepository
        
        try:
            repo_path = data_path or os.path.expanduser("~/SkipsChoreData/chores.jsonl")
            repo = ChoreRepository(repo_path)
            chore = repo.read(chore_id)
            
            if not chore:
                return {
                    "success": False,
                    "chore_id": chore_id,
                    "error": f"Chore {chore_id} not found"
                }
            
            return self.execute_chore_in_window(
                chore_id=chore.id,
                chore_name=chore.name,
                chore_description=chore.description,
                session_id=session_id
            )
            
        except Exception as e:
            logger.error(f"Repository chore execution failed: {e}")
            return {
                "success": False,
                "chore_id": chore_id,
                "error": str(e)
            }
    
    def get_execution_status(self, chore_id: int) -> Dict[str, Any]:
        """Get execution status for a chore."""
        windows = self.tmux.list_chore_windows()
        
        for window in windows:
            if window['chore_id'] == chore_id:
                return {
                    "chore_id": chore_id,
                    "status": "running",
                    "window_name": window['window_name'],
                    "session_name": self.tmux.session_name
                }
        
        return {
            "chore_id": chore_id,
            "status": "not_running"
        }
    
    def stop_chore_execution(self, chore_id: int) -> bool:
        """Stop chore execution by removing its window."""
        return self.tmux.remove_chore_window(chore_id)
    
    def list_executing_chores(self) -> list:
        """List all currently executing chores."""
        windows = self.tmux.list_chore_windows()
        return [
            {
                "chore_id": window['chore_id'],
                "window_name": window['window_name'],
                "status": "executing"
            }
            for window in windows
        ]


# Integration function for easy usage
def execute_chore_automatically(chore_id: int, chore_name: str, chore_description: str, 
                               session_name: str = "chores") -> Dict[str, Any]:
    """Execute chore automatically in TMUX window."""
    executor = ChoreExecutor(session_name)
    return executor.execute_chore_in_window(chore_id, chore_name, chore_description)


if __name__ == "__main__":
    # Test automatic execution
    executor = ChoreExecutor()
    
    # Test with demo chore
    result = executor.execute_chore_in_window(
        chore_id=99999,
        chore_name="Test Automatic Execution",
        chore_description="List main project directory",
    )
    
    print("=== Automatic Chore Execution Test ===")
    print(f"Success: {result.get('success', False)}")
    if result.get('success'):
        print(f"Command: {result['command']}")
        print(f"Session: {result['session_name']}")
        print(f"Window: {result['window_name']}")
        print(f"Attach: {result['attach_command']}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
