# TMUX Chore Integration

Add chore status to your TMUX configuration.

## Installation

1. Copy `tmux_chore_status.py` to your PATH or reference full path
2. Add to your `.tmux.conf`:

```bash
# Chore status in status bar
set -g status-right "#(python3 /path/to/tmux_chore_status.py) | %H:%M %d-%b-%y"

# Or show current chore details
set -g status-right "#(python3 /path/to/tmux_chore_status.py --current) | %H:%M"
```

3. Reload TMUX: `tmux source-file ~/.tmux.conf`

## Display Formats

- **Summary**: `Chores[WRK:1 DSN:1]` - Shows count by status
- **Current**: `TMUX Integration [WRK]` - Shows first chore details

## Status Codes

- DSN: Design
- D-R: Design Review  
- D-OK: Design Ready
- PLN: Plan
- P-R: Plan Review
- P-OK: Plan Ready
- WRK: Work
- W-R: Work Review
