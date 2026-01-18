#!/usr/bin/env python3
"""
Chore CLI - Command-line interface for chore management system

Usage:
    chore create "Task name" "Description"
    chore list [--status=STATUS]
    chore update <ID> [--name=""] [--desc=""]
    chore delete <ID>
    chore replace <ID> "New name" "New desc"
    chore -do <ID>
"""

import argparse
import sys
import os
from typing import Optional, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chore_repository import ChoreRepository
from chore import ChoreStatus
from chore_executor import ChoreExecutor
from tmux_window_manager import TMUXWindowManager


class ChoreCLI:
    """Command-line interface for chore management."""
    
    def __init__(self, data_path: str = None):
        self.data_path = data_path or os.path.expanduser("~/SkipsChoreData/chores.jsonl")
        self.repo = ChoreRepository(self.data_path)
        self.executor = ChoreExecutor()
        self.tmux = TMUXWindowManager()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with all commands."""
        parser = argparse.ArgumentParser(
            prog='chore',
            description='Chore management system with intelligent TMUX integration',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  chore create "Implement login" "Add user authentication system"
  chore list --status=work
  chore update 12345 --name="New task name"
  chore delete 12345
  chore replace 12345 "Completely new task" "New description"
  chore -do 12345
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Create command
        create_parser = subparsers.add_parser('create', help='Create a new chore')
        create_parser.add_argument('name', help='Chore name')
        create_parser.add_argument('description', nargs='?', default='', help='Chore description')
        
        # List command
        list_parser = subparsers.add_parser('list', help='List chores')
        list_parser.add_argument('--status', help='Filter by status')
        list_parser.add_argument('--all', action='store_true', help='Show all chores including completed')
        
        # Sessions command - show TMUX sessions
        sessions_parser = subparsers.add_parser('sessions', help='Show TMUX sessions and windows')
        sessions_parser.add_argument('--attach', help='Attach to specific session')
        
        # Update command
        update_parser = subparsers.add_parser('update', help='Update a chore')
        update_parser.add_argument('id', type=int, help='Chore ID')
        update_parser.add_argument('--name', help='New chore name')
        update_parser.add_argument('--desc', help='New chore description')
        update_parser.add_argument('--status', help='New chore status')
        
        # Delete command
        delete_parser = subparsers.add_parser('delete', help='Delete a chore')
        delete_parser.add_argument('id', type=int, help='Chore ID')
        delete_parser.add_argument('--force', action='store_true', help='Skip confirmation')
        
        # Replace command
        replace_parser = subparsers.add_parser('replace', help='Replace a chore completely')
        replace_parser.add_argument('id', type=int, help='Chore ID')
        replace_parser.add_argument('name', help='New chore name')
        replace_parser.add_argument('description', nargs='?', default='', help='New chore description')
        
        # Special -do command (handled separately)
        parser.add_argument('-do', '--do', type=int, dest='execute_id', 
                          help='Execute chore in TMUX window')
        
        return parser
    
    def cmd_create(self, args) -> int:
        """Handle create command."""
        try:
            chore = self.repo.create(args.name, args.description)
            print(f"Created chore {chore.id}: {chore.name}")
            return 0
        except Exception as e:
            print(f"Error creating chore: {e}", file=sys.stderr)
            return 1
    
    def cmd_list(self, args) -> int:
        """Handle list command."""
        try:
            if args.status:
                try:
                    status = ChoreStatus(args.status.lower())
                    chores = self.repo.find_by_status(status)
                except ValueError:
                    print(f"Invalid status: {args.status}", file=sys.stderr)
                    return 1
            else:
                chores = self.repo.list_all()
            
            if not chores:
                print("No chores found")
                return 0
            
            print(f"{'ID':<20} {'Status':<12} {'Name'}")
            print("-" * 60)
            for chore in chores:
                print(f"{chore.id:<20} {chore.status.value.upper():<12} {chore.name}")
            
            return 0
        except Exception as e:
            print(f"Error listing chores: {e}", file=sys.stderr)
            return 1
    
    def cmd_update(self, args) -> int:
        """Handle update command."""
        try:
            chore = self.repo.read(args.id)
            if not chore:
                print(f"Chore {args.id} not found", file=sys.stderr)
                return 1
            
            # Prepare update parameters
            update_params = {'chore_id': args.id}
            if args.name:
                update_params['name'] = args.name
            if args.desc:
                update_params['description'] = args.desc
            if args.status:
                try:
                    update_params['status'] = ChoreStatus(args.status.lower())
                except ValueError:
                    print(f"Invalid status: {args.status}", file=sys.stderr)
                    return 1
            
            updated_chore = self.repo.update(**update_params)
            if updated_chore:
                print(f"Updated chore {args.id}: {updated_chore.name}")
                return 0
            else:
                print(f"Failed to update chore {args.id}", file=sys.stderr)
                return 1
                
        except Exception as e:
            print(f"Error updating chore: {e}", file=sys.stderr)
            return 1
    
    def cmd_delete(self, args) -> int:
        """Handle delete command."""
        try:
            chore = self.repo.read(args.id)
            if not chore:
                print(f"Chore {args.id} not found", file=sys.stderr)
                return 1
            
            if not args.force:
                response = input(f"Delete chore {args.id}: {chore.name}? (y/N): ")
                if response.lower() != 'y':
                    print("Cancelled")
                    return 0
            
            if self.repo.delete(args.id):
                print(f"Deleted chore {args.id}")
                return 0
            else:
                print(f"Failed to delete chore {args.id}", file=sys.stderr)
                return 1
                
        except Exception as e:
            print(f"Error deleting chore: {e}", file=sys.stderr)
            return 1
    
    def cmd_replace(self, args) -> int:
        """Handle replace command."""
        try:
            chore = self.repo.read(args.id)
            if not chore:
                print(f"Chore {args.id} not found", file=sys.stderr)
                return 1
            
            updated_chore = self.repo.update(args.id, name=args.name, description=args.description)
            if updated_chore:
                print(f"Replaced chore {args.id}: {updated_chore.name}")
                return 0
            else:
                print(f"Failed to replace chore {args.id}", file=sys.stderr)
                return 1
                
        except Exception as e:
            print(f"Error replacing chore: {e}", file=sys.stderr)
            return 1
    
    def cmd_sessions(self, args) -> int:
        """Handle sessions command - show TMUX sessions."""
        try:
            if args.attach:
                # Attach to specific session
                result = self.tmux.attach_to_session(args.attach)
                if result:
                    print(f"Attached to session: {args.attach}")
                    return 0
                else:
                    print(f"Failed to attach to session: {args.attach}", file=sys.stderr)
                    return 1
            
            # Show current TMUX context
            current_session = self.tmux.get_current_session()
            if current_session:
                print(f"Current session: {current_session}")
            else:
                print("Not in TMUX session")
            
            # List all sessions
            sessions = self.tmux.list_sessions()
            if sessions:
                print("\nAvailable sessions:")
                for session in sessions:
                    windows = self.tmux.list_windows(session)
                    print(f"  {session} ({len(windows)} windows)")
                    for window in windows[:3]:  # Show first 3 windows
                        print(f"    - {window}")
                    if len(windows) > 3:
                        print(f"    ... and {len(windows) - 3} more")
            else:
                print("\nNo TMUX sessions found")
            
            return 0
        except Exception as e:
            print(f"Error accessing TMUX sessions: {e}", file=sys.stderr)
            return 1

    def cmd_execute(self, chore_id: int) -> int:
        """Handle -do command (smart TMUX execution)."""
        try:
            result = self.executor.execute_chore_from_repository(chore_id, data_path=self.data_path)
            
            if result['success']:
                print(f"Executing chore {chore_id} in TMUX window")
                print(f"Session: {result['session_name']}")
                print(f"Window: {result['window_name']}")
                print(f"Attach: {result['attach_command']}")
                return 0
            else:
                print(f"Failed to execute chore {chore_id}: {result.get('error', 'Unknown error')}", file=sys.stderr)
                return 1
                
        except Exception as e:
            print(f"Error executing chore: {e}", file=sys.stderr)
            return 1
        """Handle -do command (smart TMUX execution)."""
        try:
            result = self.executor.execute_chore_from_repository(chore_id)
            
            if result['success']:
                print(f"Executing chore {chore_id} in TMUX window")
                print(f"Session: {result['session_name']}")
                print(f"Window: {result['window_name']}")
                print(f"Attach: {result['attach_command']}")
                return 0
            else:
                print(f"Failed to execute chore {chore_id}: {result.get('error', 'Unknown error')}", file=sys.stderr)
                return 1
                
        except Exception as e:
            print(f"Error executing chore: {e}", file=sys.stderr)
            return 1
    
    def run(self, args: List[str] = None) -> int:
        """Run the CLI with given arguments."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        # Handle -do command first
        if parsed_args.execute_id:
            return self.cmd_execute(parsed_args.execute_id)
        
        # Handle subcommands
        if not parsed_args.command:
            parser.print_help()
            return 1
        
        command_handlers = {
            'create': self.cmd_create,
            'list': self.cmd_list,
            'update': self.cmd_update,
            'delete': self.cmd_delete,
            'replace': self.cmd_replace,
            'sessions': self.cmd_sessions,
        }
        
        handler = command_handlers.get(parsed_args.command)
        if handler:
            return handler(parsed_args)
        else:
            print(f"Unknown command: {parsed_args.command}", file=sys.stderr)
            return 1


def main():
    """Main entry point for CLI."""
    cli = ChoreCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
