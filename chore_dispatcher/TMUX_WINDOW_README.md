# TMUX Window-Based Chore Management

Dynamic TMUX window creation for active chore workflow integration.

## Overview

The TMUX Window Manager creates dedicated TMUX windows for active chores, providing isolated workspaces for each task. Windows are created in existing sessions or new sessions are spawned as needed.

## Core Features

- **Session Detection**: Automatically detects existing TMUX sessions
- **Dynamic Windows**: Creates dedicated windows for active chores  
- **Workspace Isolation**: Each chore gets its own terminal environment
- **Automatic Cleanup**: Removes windows when chores complete

## Installation

### Prerequisites
- TMUX 2.1 or later
- Python 3.6 or later
- Chore Dispatcher system

### Install TMUX

**macOS (Homebrew):**
```bash
brew install tmux
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tmux
```

**CentOS/RHEL:**
```bash
sudo yum install tmux
```

**Verify installation:**
```bash
tmux -V  # Should show version 2.1 or later
```

## Usage

### Automatic Integration

The TMUX Window Manager integrates automatically with the chore lifecycle:

```python
from tmux_window_manager import TMUXWindowManager

# Initialize manager
manager = TMUXWindowManager()

# Create window for active chore
manager.create_chore_window(chore_id=12345, chore_name="Implement user authentication")

# Remove window when chore completes
manager.remove_chore_window(chore_id=12345)
```

### Manual Operations

**Create chore session:**
```python
from tmux_window_manager import TMUXWindowManager

manager = TMUXWindowManager(session_name="my_chores")
if not manager.has_existing_session():
    manager.create_session()
```

**List active chore windows:**
```python
windows = manager.list_chore_windows()
for window in windows:
    print(f"Chore {window['chore_id']}: {window['window_name']}")
```

## Window Management

### Session Behavior
- **Existing Session**: Creates new windows in current session
- **No Session**: Creates new session named "chores" (default)
- **Custom Session**: Specify session name in constructor

### Window Naming
- **Format**: `chore_{chore_id}`
- **Title**: Truncated chore name (30 chars max)
- **Example**: Window "chore_12345" with title "Implement user auth..."

### Lifecycle Integration
- **Window Creation**: Triggered when chore enters WORK phase
- **Window Removal**: Triggered when chore reaches WORK_DONE
- **Error Handling**: Graceful fallback if TMUX unavailable

## Configuration

### Custom Session Name
```python
manager = TMUXWindowManager(session_name="development")
```

### Integration with ChoreRepository
```python
from chore_repository import ChoreRepository
from tmux_window_manager import integrate_with_chore_lifecycle

repo = ChoreRepository()
tmux_manager = integrate_with_chore_lifecycle()

# Windows automatically managed during chore lifecycle
```

## TMUX Commands Reference

The system uses these TMUX commands internally:

```bash
# Session management
tmux list-sessions                    # Detect existing sessions
tmux new-session -d -s chores        # Create detached session

# Window management  
tmux new-window -t chores -n chore_123    # Create named window
tmux rename-window -t chores:chore_123 "Title"  # Set window title
tmux kill-window -t chores:chore_123      # Remove window
tmux list-windows -t chores -F '#{window_name}'  # List windows
```

## Troubleshooting

### TMUX Not Available
If TMUX is not installed, the system gracefully degrades:
- `has_existing_session()` returns `False`
- `create_session()` returns `False`  
- Window operations return `False`
- No errors thrown, system continues normally

### Session Not Found
If the target session doesn't exist:
- System automatically creates new session
- Windows are created in the new session
- Default session name is "chores"

### Window Already Exists
If a window with the same chore ID exists:
- New window creation may fail silently
- Use `list_chore_windows()` to check existing windows
- Remove existing window before creating new one

## Integration Examples

### Basic Chore Workflow
```python
from chore_repository import ChoreRepository
from tmux_window_manager import TMUXWindowManager

repo = ChoreRepository()
tmux = TMUXWindowManager()

# Create chore
chore = repo.create("Implement API endpoint", "REST API for user data")

# Create TMUX window for work
tmux.create_chore_window(chore.id, chore.name)

# Work in dedicated window...
# (User switches to TMUX window for development)

# Complete chore and cleanup
repo.update(chore.id, status=ChoreStatus.WORK_DONE)
tmux.remove_chore_window(chore.id)
```

### Batch Window Management
```python
# Create windows for all active chores
active_chores = repo.find_by_status(ChoreStatus.WORK)
for chore in active_chores:
    tmux.create_chore_window(chore.id, chore.name)

# Cleanup completed chores
completed_chores = repo.find_by_status(ChoreStatus.WORK_DONE)
for chore in completed_chores:
    tmux.remove_chore_window(chore.id)
```

This window-based approach provides dedicated workspaces for each chore, improving focus and organization during development workflows.
