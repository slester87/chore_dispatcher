#!/usr/bin/env python3
"""
Enhanced Chore CLI with configuration and improved UX
"""

import argparse
import sys
import os
import json
from typing import Optional, List, Dict, Any
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chore_repository import ChoreRepository
from chore import ChoreStatus
from chore_executor import ChoreExecutor
from tmux_window_manager import TMUXWindowManager


class ChoreConfig:
    """Configuration management for Chore CLI."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.expanduser("~/.chore_config.json")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Default configuration
        return {
            "data_path": "~/SkipsChoreData/chores.jsonl",
            "default_session": "chores",
            "colors": True,
            "auto_attach": False,
            "confirm_delete": True
        }
    
    def save_config(self):
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError:
            pass
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value
        self.save_config()


class ColorOutput:
    """Colored terminal output."""
    
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bold': '\033[1m',
        'end': '\033[0m'
    }
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
    
    def color(self, text: str, color: str) -> str:
        """Apply color to text."""
        if not self.enabled:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['end']}"
    
    def status_color(self, status: str) -> str:
        """Get color for chore status."""
        status_colors = {
            'design': 'blue',
            'design_review': 'cyan',
            'design_ready': 'green',
            'plan': 'yellow',
            'plan_review': 'magenta',
            'plan_ready': 'green',
            'work': 'bold',
            'work_review': 'cyan',
            'work_done': 'green'
        }
        return status_colors.get(status.lower(), 'white')


class EnhancedChoreCLI:
    """Enhanced CLI with configuration and improved UX."""
    
    def __init__(self, config_path: str = None):
        self.config = ChoreConfig(config_path)
        self.colors = ColorOutput(self.config.get('colors', True))
        
        data_path = os.path.expanduser(self.config.get('data_path'))
        self.repo = ChoreRepository(data_path)
        self.executor = ChoreExecutor()
        self.tmux = TMUXWindowManager(self.config.get('default_session', 'chores'))
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create enhanced argument parser."""
        parser = argparse.ArgumentParser(
            prog='chore',
            description='Enhanced chore management with TMUX integration',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  chore create "Implement login" "Add authentication"
  chore list --status=work --color
  chore config --set colors=false
  chore -do 12345 --attach
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Commands')
        
        # Create command
        create_parser = subparsers.add_parser('create', help='Create chore')
        create_parser.add_argument('name', help='Chore name')
        create_parser.add_argument('description', nargs='?', default='', help='Description')
        
        # List command
        list_parser = subparsers.add_parser('list', help='List chores')
        list_parser.add_argument('--status', help='Filter by status')
        list_parser.add_argument('--color', action='store_true', help='Force colored output')
        list_parser.add_argument('--no-color', action='store_true', help='Disable colors')
        
        # Update command
        update_parser = subparsers.add_parser('update', help='Update chore')
        update_parser.add_argument('id', type=int, help='Chore ID')
        update_parser.add_argument('--name', help='New name')
        update_parser.add_argument('--desc', help='New description')
        update_parser.add_argument('--status', help='New status')
        
        # Delete command
        delete_parser = subparsers.add_parser('delete', help='Delete chore')
        delete_parser.add_argument('id', type=int, help='Chore ID')
        delete_parser.add_argument('--force', action='store_true', help='Skip confirmation')
        
        # Replace command
        replace_parser = subparsers.add_parser('replace', help='Replace chore')
        replace_parser.add_argument('id', type=int, help='Chore ID')
        replace_parser.add_argument('name', help='New name')
        replace_parser.add_argument('description', nargs='?', default='', help='New description')
        
        # Sessions command
        sessions_parser = subparsers.add_parser('sessions', help='TMUX sessions')
        sessions_parser.add_argument('--attach', help='Attach to session')
        
        # Config command
        config_parser = subparsers.add_parser('config', help='Configuration')
        config_parser.add_argument('--set', help='Set config: key=value')
        config_parser.add_argument('--get', help='Get config value')
        config_parser.add_argument('--list', action='store_true', help='List all config')
        
        # Archive command
        archive_parser = subparsers.add_parser('archive', help='Archive completed chores')
        archive_parser.add_argument('--dry-run', action='store_true', help='Show what would be archived')
        
        # Execute command
        parser.add_argument('-do', '--do', type=int, dest='execute_id', help='Execute chore')
        parser.add_argument('--attach', action='store_true', help='Auto-attach to session')
        
        return parser
    
    def cmd_list(self, args) -> int:
        """Enhanced list with colors and formatting."""
        try:
            # Handle color options
            if args.color:
                self.colors.enabled = True
            elif args.no_color:
                self.colors.enabled = False
            
            if args.status:
                try:
                    status = ChoreStatus(args.status.lower())
                    chores = self.repo.find_by_status(status)
                except ValueError:
                    print(self.colors.color(f"Invalid status: {args.status}", 'red'), file=sys.stderr)
                    return 1
            else:
                chores = self.repo.list_all()
            
            if not chores:
                print(self.colors.color("No chores found", 'yellow'))
                return 0
            
            # Enhanced table output
            print(f"{'ID':<20} {'Status':<12} {'Name'}")
            print(self.colors.color("-" * 60, 'cyan'))
            
            for chore in chores:
                status_text = chore.status.value.upper()
                colored_status = self.colors.color(status_text, self.colors.status_color(status_text))
                print(f"{chore.id:<20} {colored_status:<20} {chore.name}")
            
            return 0
        except Exception as e:
            print(self.colors.color(f"Error: {e}", 'red'), file=sys.stderr)
            return 1
    
    def cmd_config(self, args) -> int:
        """Handle configuration commands."""
        try:
            if args.set:
                if '=' not in args.set:
                    print(self.colors.color("Format: key=value", 'red'), file=sys.stderr)
                    return 1
                
                key, value = args.set.split('=', 1)
                # Convert boolean strings
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                
                self.config.set(key, value)
                print(self.colors.color(f"Set {key} = {value}", 'green'))
                return 0
            
            elif args.get:
                value = self.config.get(args.get)
                print(f"{args.get} = {value}")
                return 0
            
            elif args.list:
                print(self.colors.color("Configuration:", 'bold'))
                for key, value in self.config.config.items():
                    print(f"  {key} = {value}")
                return 0
            
            else:
                print("Use --set, --get, or --list")
                return 1
                
        except Exception as e:
            print(self.colors.color(f"Config error: {e}", 'red'), file=sys.stderr)
            return 1
    
    def cmd_archive(self, args) -> int:
        """Handle archive command."""
        try:
            from archive_chores import archive_completed_chores
            
            data_path = os.path.expanduser(self.config.get('data_path'))
            completed_chores = self.repo.find_by_status(ChoreStatus.WORK_DONE)
            
            if not completed_chores:
                print(self.colors.color("No completed chores to archive", 'yellow'))
                return 0
            
            if args.dry_run:
                print(self.colors.color(f"Would archive {len(completed_chores)} chores:", 'cyan'))
                for chore in completed_chores:
                    print(f"  📦 {chore.id}: {chore.name}")
                return 0
            
            archived_count = archive_completed_chores(data_path)
            if archived_count > 0:
                print(self.colors.color(f"✅ Archived {archived_count} completed chores", 'green'))
            
            return 0
        except Exception as e:
            print(self.colors.color(f"Archive error: {e}", 'red'), file=sys.stderr)
            return 1

    def cmd_execute(self, chore_id: int, auto_attach: bool = False) -> int:
        """Enhanced execute with auto-attach option."""
        try:
            data_path = os.path.expanduser(self.config.get('data_path'))
            result = self.executor.execute_chore_from_repository(chore_id, data_path=data_path)
            
            if result['success']:
                print(self.colors.color(f"✓ Executing chore {chore_id}", 'green'))
                print(f"Session: {self.colors.color(result['session_name'], 'cyan')}")
                print(f"Window: {result['window_name']}")
                
                if auto_attach or self.config.get('auto_attach', False):
                    print(self.colors.color("Auto-attaching to session...", 'yellow'))
                    os.system(result['attach_command'])
                else:
                    print(f"Attach: {self.colors.color(result['attach_command'], 'blue')}")
                
                return 0
            else:
                print(self.colors.color(f"✗ Failed: {result.get('error', 'Unknown error')}", 'red'), file=sys.stderr)
                return 1
                
        except Exception as e:
            print(self.colors.color(f"Error: {e}", 'red'), file=sys.stderr)
            return 1
    
    def run(self, args: List[str] = None) -> int:
        """Run enhanced CLI."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        # Handle execute command
        if parsed_args.execute_id:
            return self.cmd_execute(parsed_args.execute_id, parsed_args.attach)
        
        if not parsed_args.command:
            parser.print_help()
            return 1
        
        # Enhanced command handlers
        if parsed_args.command == 'list':
            return self.cmd_list(parsed_args)
        elif parsed_args.command == 'config':
            return self.cmd_config(parsed_args)
        elif parsed_args.command == 'archive':
            return self.cmd_archive(parsed_args)
        
        # Fallback to basic CLI for other commands
        from chore_cli import ChoreCLI
        basic_cli = ChoreCLI(os.path.expanduser(self.config.get('data_path')))
        return basic_cli.run(args)


def main():
    """Enhanced CLI entry point."""
    cli = EnhancedChoreCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
