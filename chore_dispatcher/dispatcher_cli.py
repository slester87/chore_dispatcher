#!/usr/bin/env python3
"""
Dispatcher CLI Commands

Management commands for TMUX chore dispatcher.
"""

import argparse
import sys
from typing import Optional
from chore_dispatcher import ChoreDispatcher
from dispatcher_hooks import get_dispatcher_hooks

def add_dispatcher_commands(parser: argparse.ArgumentParser) -> None:
    """Add dispatcher commands to CLI parser."""
    dispatcher_parser = parser.add_subparsers(dest='dispatcher_command')
    
    # Status command
    status_parser = dispatcher_parser.add_parser('status', help='Show dispatcher status')
    
    # Attach command  
    attach_parser = dispatcher_parser.add_parser('attach', help='Attach to dispatcher session')
    attach_parser.add_argument('chore_id', type=int, nargs='?', help='Chore ID to focus')
    
    # Cleanup command
    cleanup_parser = dispatcher_parser.add_parser('cleanup', help='Clean up orphaned windows')

def handle_dispatcher_command(args: argparse.Namespace) -> int:
    """Handle dispatcher CLI commands."""
    dispatcher = ChoreDispatcher()
    
    if args.dispatcher_command == 'status':
        return _handle_status(dispatcher)
    elif args.dispatcher_command == 'attach':
        return _handle_attach(dispatcher, args.chore_id)
    elif args.dispatcher_command == 'cleanup':
        return _handle_cleanup(dispatcher)
    else:
        print("Unknown dispatcher command", file=sys.stderr)
        return 1

def _handle_status(dispatcher: ChoreDispatcher) -> int:
    """Handle status command."""
    try:
        windows = dispatcher.list_active_windows()
        
        if not windows:
            print("No active chore windows")
            return 0
            
        print(f"Active windows in session '{dispatcher.session_name}':")
        for window in windows:
            status = "ACTIVE" if window['active'] else "inactive"
            print(f"  {window['name']} ({status})")
            
        return 0
        
    except Exception as e:
        print(f"Failed to get status: {e}", file=sys.stderr)
        return 1

def _handle_attach(dispatcher: ChoreDispatcher, chore_id: Optional[int]) -> int:
    """Handle attach command."""
    try:
        if chore_id:
            # Focus specific chore window
            windows = dispatcher.list_active_windows()
            target_window = None
            
            for window in windows:
                if window['name'].startswith(f"chore-{chore_id}-"):
                    target_window = window['name']
                    break
                    
            if not target_window:
                print(f"No window found for chore {chore_id}", file=sys.stderr)
                return 1
                
            # Select window and attach
            import subprocess
            subprocess.run([
                "tmux", "select-window", "-t", f"{dispatcher.session_name}:{target_window}"
            ], check=True)
            
        # Attach to session
        return 0 if dispatcher.attach_to_session() else 1
        
    except Exception as e:
        print(f"Failed to attach: {e}", file=sys.stderr)
        return 1

def _handle_cleanup(dispatcher: ChoreDispatcher) -> int:
    """Handle cleanup command."""
    try:
        windows = dispatcher.list_active_windows()
        
        if not windows:
            print("No windows to clean up")
            return 0
            
        # For now, just list windows - actual cleanup would need chore status checking
        print("Active chore windows:")
        for window in windows:
            print(f"  {window['name']}")
            
        print("\nUse 'chore dispatcher status' to see current state")
        print("Individual windows are cleaned up automatically when chores complete")
        
        return 0
        
    except Exception as e:
        print(f"Failed to cleanup: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    # Simple test interface
    parser = argparse.ArgumentParser(description="Chore Dispatcher CLI")
    add_dispatcher_commands(parser)
    
    args = parser.parse_args()
    sys.exit(handle_dispatcher_command(args))
