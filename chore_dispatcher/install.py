#!/usr/bin/env python3
"""
Chore CLI Installation Script
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def create_executable_script():
    """Create standalone executable script."""
    script_content = '''#!/usr/bin/env python3
"""
Chore CLI - Standalone executable
"""

import sys
import os

# Add the chore_dispatcher directory to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHORE_DIR = os.path.join(SCRIPT_DIR, 'chore_system', 'chore_dispatcher')
sys.path.insert(0, CHORE_DIR)

try:
    from chore_enhanced import main
    sys.exit(main())
except ImportError:
    # Fallback to basic CLI
    from chore_cli import main
    sys.exit(main())
'''
    
    return script_content


def install_cli():
    """Install chore CLI system."""
    print("🚀 Installing Chore CLI...")
    
    # Get installation directory
    install_dir = os.path.expanduser("~/bin")
    os.makedirs(install_dir, exist_ok=True)
    
    # Current directory (should be chore_dispatcher)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Create installation target
    target_dir = os.path.join(install_dir, "chore_system")
    
    # Copy chore_dispatcher directory
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    
    shutil.copytree(current_dir, os.path.join(target_dir, "chore_dispatcher"))
    
    # Create executable script
    executable_path = os.path.join(install_dir, "chore")
    script_content = create_executable_script()
    
    with open(executable_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(executable_path, 0o755)
    
    print(f"✅ Installed to: {install_dir}")
    print(f"✅ Executable: {executable_path}")
    
    # Check if ~/bin is in PATH
    path_dirs = os.environ.get('PATH', '').split(':')
    if install_dir not in path_dirs:
        print(f"\n⚠️  Add to PATH:")
        print(f"   echo 'export PATH=\"$PATH:{install_dir}\"' >> ~/.bashrc")
        print(f"   echo 'export PATH=\"$PATH:{install_dir}\"' >> ~/.zshrc")
        print(f"   source ~/.bashrc  # or ~/.zshrc")
        print(f"\n   Or run: export PATH=\"$PATH:{install_dir}\"")
    else:
        print(f"\n✅ {install_dir} already in PATH")
    
    print(f"\n🎯 Usage:")
    print(f"   chore create \"Task name\" \"Description\"")
    print(f"   chore list --color")
    print(f"   chore -do <ID> --attach")
    print(f"   chore config --list")
    
    return True


def create_setup_py():
    """Create setup.py for pip installation."""
    setup_content = '''#!/usr/bin/env python3
"""
Setup script for Chore CLI
"""

from setuptools import setup, find_packages

setup(
    name="chore-cli",
    version="1.0.0",
    description="Chore management system with TMUX integration",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'chore=chore_dispatcher.chore_enhanced:main',
        ],
    },
    python_requires='>=3.7',
    install_requires=[],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7+",
    ],
)
'''
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    setup_path = os.path.join(project_root, "setup.py")
    
    with open(setup_path, 'w') as f:
        f.write(setup_content)
    
    print(f"✅ Created setup.py: {setup_path}")
    return setup_path


def create_readme():
    """Create installation README."""
    readme_content = '''# Chore CLI Installation

## Quick Install

```bash
# Clone and install
git clone <repository-url>
cd chore_dispatcher
python3 install.py

# Or use pip (if setup.py exists)
pip install -e .
```

## Usage

```bash
# Create chores
chore create "Implement feature" "Add user authentication"

# List chores with colors
chore list --color --status=work

# Execute chore in TMUX
chore -do 12345 --attach

# Configure system
chore config --set colors=true
chore config --set auto_attach=true
```

## Features

- ✅ Complete CRUD operations
- ✅ Intelligent TMUX integration
- ✅ Colored output and configuration
- ✅ Smart session management
- ✅ Automatic command execution

## Requirements

- Python 3.7+
- TMUX (for execution features)
- Unix-like system (macOS, Linux)
'''
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    readme_path = os.path.join(project_root, "INSTALL.md")
    
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"✅ Created INSTALL.md: {readme_path}")
    return readme_path


def main():
    """Main installation function."""
    print("Chore CLI Installation System")
    print("=" * 40)
    
    try:
        # Install CLI
        install_cli()
        
        # Create setup.py for pip installation
        create_setup_py()
        
        # Create installation README
        create_readme()
        
        print("\n🎉 Installation complete!")
        print("\nTest installation:")
        print("   chore --help")
        print("   chore list")
        
        return 0
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
