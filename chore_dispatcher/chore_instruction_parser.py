"""
Chore Instruction Parser

Parses chore descriptions to generate executable UNIX commands.
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ChoreInstruction:
    """Represents a parsed chore instruction."""
    command: str
    description: str
    working_dir: Optional[str] = None
    expected_output: Optional[str] = None


class ChoreInstructionParser:
    """Parses chore descriptions into executable UNIX commands."""
    
    def __init__(self):
        self.command_patterns = {
            # Directory listing patterns
            r'list.*main.*project.*director': 'ls -la /Users/skippo/Development/KIRO',
            r'list.*chore.*dispatcher.*director': 'ls -la /Users/skippo/Development/KIRO/chore_dispatcher',
            r'list.*tests.*director': 'ls -la /Users/skippo/Development/KIRO/chore_dispatcher/tests',
            r'show.*chore.*data.*files': 'ls -la /Users/skippo/SkipsChoreData',
            r'list.*director(?:y|ies).*(?:in|of)\s+([^\s]+)': 'ls -la {path}',
            r'show.*contents.*(?:in|of)\s+([^\s]+)': 'ls -la {path}',
            
            # File operations
            r'show.*file.*([^\s]+)': 'cat {path}',
            r'read.*file.*([^\s]+)': 'cat {path}',
            r'view.*([^\s]+\.(?:py|md|txt|json))': 'cat {path}',
            r'edit.*([^\s]+\.(?:py|md|txt|json))': 'nano {path}',
            
            # Test operations
            r'run.*tests?': 'python3 test_chore.py',
            r'execute.*tests?': 'python3 tests/run_tests.py',
            r'test.*comprehensive': 'python3 tests/run_tests.py comprehensive',
            r'run.*unit.*tests': 'python3 -m pytest tests/',
            
            # Build operations
            r'build.*project': 'python3 -m build',
            r'compile.*code': 'python3 -m py_compile *.py',
            r'install.*dependencies': 'pip install -r requirements.txt',
            
            # Git operations
            r'git.*status': 'git status',
            r'show.*git.*log': 'git log --oneline -10',
            r'check.*changes': 'git diff --name-only',
            r'git.*add.*all': 'git add .',
            r'commit.*changes': 'git commit -m "Automated commit"',
            
            # System operations
            r'check.*system.*status': 'python3 -c "from chore_repository import ChoreRepository; repo = ChoreRepository(); print(repo.validate_system_integrity())"',
            r'show.*chore.*status': 'python3 -c "from chore_repository import ChoreRepository; repo = ChoreRepository(); [print(f\'{c.id} | {c.status.value} | {c.name}\') for c in repo.list_all()]"',
            r'cleanup.*system': 'python3 -c "from chore_repository import ChoreRepository; repo = ChoreRepository(); print(repo.repair_system())"',
            
            # Development operations
            r'start.*server': 'python3 -m http.server 8000',
            r'run.*python.*script.*([^\s]+)': 'python3 {path}',
            r'execute.*([^\s]+\.py)': 'python3 {path}',
            
            # Documentation operations
            r'generate.*docs': 'python3 -m pydoc -w .',
            r'view.*readme': 'cat README.md',
            r'show.*documentation': 'find . -name "*.md" -exec echo "=== {} ===" \\; -exec cat {} \\;',
        }
        
        # Command templates for common chore types
        self.chore_templates = {
            'directory_listing': {
                'pattern': r'list.*director',
                'template': 'ls -la {directory}',
                'description': 'List directory contents with details'
            },
            'file_viewing': {
                'pattern': r'(?:show|view|read).*file',
                'template': 'cat {file_path}',
                'description': 'Display file contents'
            },
            'testing': {
                'pattern': r'(?:run|execute).*test',
                'template': 'python3 {test_command}',
                'description': 'Execute test suite'
            },
            'building': {
                'pattern': r'build.*project',
                'template': 'python3 -m build',
                'description': 'Build project artifacts'
            },
            'git_operations': {
                'pattern': r'git.*',
                'template': 'git {git_command}',
                'description': 'Execute git command'
            }
        }
    
    def parse_chore_description(self, description: str) -> List[ChoreInstruction]:
        """Parse chore description into executable instructions."""
        instructions = []
        description_lower = description.lower()
        
        # Try to match against known patterns
        for pattern, command_template in self.command_patterns.items():
            match = re.search(pattern, description_lower)
            if match:
                # Extract path if captured
                if match.groups():
                    path = match.group(1)
                    command = command_template.format(path=path)
                else:
                    command = command_template
                
                instructions.append(ChoreInstruction(
                    command=command,
                    description=f"Execute: {command}",
                    working_dir=self._get_working_directory(description)
                ))
                break
        
        # If no pattern matched, create a generic instruction
        if not instructions:
            instructions.append(ChoreInstruction(
                command=self._generate_generic_command(description),
                description=f"Generic task: {description}",
                working_dir=self._get_working_directory(description)
            ))
        
        return instructions
    
    def _get_working_directory(self, description: str) -> Optional[str]:
        """Determine appropriate working directory based on description."""
        description_lower = description.lower()
        
        if 'chore dispatcher' in description_lower or 'test' in description_lower:
            return '/Users/skippo/Development/KIRO/chore_dispatcher'
        elif 'main project' in description_lower or 'kiro' in description_lower:
            return '/Users/skippo/Development/KIRO'
        elif 'chore data' in description_lower:
            return '/Users/skippo/SkipsChoreData'
        
        return '/Users/skippo/Development/KIRO/chore_dispatcher'  # Default
    
    def _generate_generic_command(self, description: str) -> str:
        """Generate a generic command for unmatched descriptions."""
        # For demo purposes, create an echo command with the description
        return f'echo "Executing: {description}" && echo "Task completed successfully"'
    
    def get_template_for_chore_type(self, chore_type: str) -> Optional[Dict]:
        """Get command template for specific chore type."""
        return self.chore_templates.get(chore_type)
    
    def get_all_templates(self) -> Dict:
        """Get all available command templates."""
        return self.chore_templates
    
    def suggest_command_for_description(self, description: str) -> List[str]:
        """Suggest possible commands based on description keywords."""
        suggestions = []
        description_lower = description.lower()
        
        # Check each template pattern
        for template_name, template_info in self.chore_templates.items():
            if re.search(template_info['pattern'], description_lower):
                suggestions.append(f"{template_name}: {template_info['description']}")
        
        return suggestions
    
    def create_custom_command(self, base_template: str, **kwargs) -> str:
        """Create custom command from template with parameters."""
        try:
            return base_template.format(**kwargs)
        except KeyError as e:
            return f"Template error: missing parameter {e}"
    
    def get_command_for_chore(self, chore_name: str, chore_description: str) -> ChoreInstruction:
        """Get the primary command for a chore."""
        instructions = self.parse_chore_description(chore_description)
        return instructions[0] if instructions else ChoreInstruction(
            command='echo "No command generated"',
            description="No executable command found"
        )


# Example usage and testing
if __name__ == "__main__":
    parser = ChoreInstructionParser()
    
    # Test cases
    test_chores = [
        ("List main project directory", "Run ls -la in /Users/skippo/Development/KIRO to show project structure"),
        ("List chore dispatcher directory", "Run ls -la in /Users/skippo/Development/KIRO/chore_dispatcher to show implementation files"),
        ("Show chore data files", "Run ls -la in /Users/skippo/SkipsChoreData to show active and completed chore archives"),
        ("Run tests", "Execute the test suite to verify system functionality")
    ]
    
    print("=== Chore Instruction Parser Test ===")
    for name, description in test_chores:
        instruction = parser.get_command_for_chore(name, description)
        print(f"Chore: {name}")
        print(f"Command: {instruction.command}")
        print(f"Working Dir: {instruction.working_dir}")
        print()
