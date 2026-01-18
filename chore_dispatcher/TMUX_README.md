# TMUX Chore Integration

Real-time chore status display for TMUX status bar and panes.

## Overview

The TMUX Chore Integration provides live monitoring of your active chores directly in your TMUX environment. View chore counts by status, current chore details, and workflow progress without leaving your terminal.

## Installation

### Prerequisites
- TMUX 2.1 or later
- Python 3.6 or later
- SkipsChoreData repository with active chores

### Setup Steps

1. **Copy the status script** to your preferred location:
   ```bash
   cp tmux_chore_status.py ~/.local/bin/
   chmod +x ~/.local/bin/tmux_chore_status.py
   ```

2. **Add to your `.tmux.conf`** (choose one format):

   **Summary Format** - Shows count by status:
   ```bash
   set -g status-right "#(python3 ~/.local/bin/tmux_chore_status.py) | %H:%M %d-%b-%y"
   ```

   **Current Chore Format** - Shows first active chore:
   ```bash
   set -g status-right "#(python3 ~/.local/bin/tmux_chore_status.py --current) | %H:%M"
   ```

3. **Reload TMUX configuration**:
   ```bash
   tmux source-file ~/.tmux.conf
   ```

## Display Formats

### Summary Format
Shows aggregated chore counts by workflow status:
```
Chores[WRK:2 DSN:1 P-R:1]
```

### Current Chore Format  
Shows details of the first active chore:
```
TMUX Integration [WRK]
```

Long chore names are truncated with ellipsis for space efficiency.

## Status Code Reference

| Code | Status | Description |
|------|--------|-------------|
| DSN  | design | Initial design phase |
| D-R  | design_review | Design under review |
| D-OK | design_ready | Design approved |
| PLN  | plan | Implementation planning |
| P-R  | plan_review | Plan under review |
| P-OK | plan_ready | Plan approved |
| WRK  | work | Active development |
| W-R  | work_review | Work under review |

## Configuration Options

### Custom Refresh Rate
TMUX refreshes status every 15 seconds by default. To change:
```bash
set -g status-interval 5  # Refresh every 5 seconds
```

### Custom Status Position
```bash
# Left side status
set -g status-left "#(python3 ~/.local/bin/tmux_chore_status.py) | "

# Both sides
set -g status-left "#(python3 ~/.local/bin/tmux_chore_status.py --current)"
set -g status-right "#(python3 ~/.local/bin/tmux_chore_status.py) | %H:%M"
```

### Color Customization
```bash
# Highlight chore status in color
set -g status-right "#[fg=cyan]#(python3 ~/.local/bin/tmux_chore_status.py)#[default] | %H:%M"
```

## Advanced Usage

### Dedicated Chore Pane
Create a dedicated pane for chore monitoring:
```bash
# In TMUX session
tmux split-window -h
tmux send-keys "watch -n 5 'python3 ~/.local/bin/tmux_chore_status.py --current && echo && python3 ~/.local/bin/tmux_chore_status.py'" Enter
```

### Integration with Other Tools
```bash
# Combine with git status
set -g status-right "#(python3 ~/.local/bin/tmux_chore_status.py) | #(git branch --show-current 2>/dev/null || echo 'no-git') | %H:%M"
```

## Troubleshooting

### No Chores Displayed
- **Check file path**: Ensure `~/SkipsChoreData/chores.jsonl` exists
- **Verify permissions**: Script must be executable
- **Test manually**: Run script directly to see output

### Script Errors
```bash
# Test script execution
python3 ~/.local/bin/tmux_chore_status.py
python3 ~/.local/bin/tmux_chore_status.py --current

# Check for Python errors
python3 -c "import json, os; print('Python OK')"
```

### Status Not Updating
- **Reload TMUX config**: `tmux source-file ~/.tmux.conf`
- **Check refresh interval**: Verify `status-interval` setting
- **Restart TMUX**: Exit and restart TMUX session

### Path Issues
If script not found, use full path:
```bash
set -g status-right "#(/usr/bin/python3 /full/path/to/tmux_chore_status.py) | %H:%M"
```

## File Locations

- **Script**: `tmux_chore_status.py`
- **Data Source**: `~/SkipsChoreData/chores.jsonl`
- **Config**: `~/.tmux.conf`

## Performance Notes

- Script execution time: ~10ms typical
- Memory usage: Minimal (~2MB Python process)
- Network: No network calls (local file only)
- CPU: Negligible impact on system performance

## Examples

### Minimal Setup
```bash
# Simple right-side status
set -g status-right "#(python3 ~/.local/bin/tmux_chore_status.py)"
```

### Full Status Bar
```bash
# Comprehensive status with time and chores
set -g status-left "#S | "
set -g status-right "#(python3 ~/.local/bin/tmux_chore_status.py) | %H:%M %d-%b-%y"
set -g status-interval 10
```

### Development Workflow
```bash
# Show current chore and git branch
set -g status-right "#(python3 ~/.local/bin/tmux_chore_status.py --current) | #(git branch --show-current 2>/dev/null) | %H:%M"
```

The cosmos of your chores, visible at a glance.
