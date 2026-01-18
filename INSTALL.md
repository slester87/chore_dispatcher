# Chore CLI Installation

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
