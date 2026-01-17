#!/usr/bin/env python3
"""
TMUX Chore Status Display
Displays active chore information in TMUX status bar
"""

import json
import sys
import os
from pathlib import Path

def load_active_chores(chores_file):
    """Load active chores from JSON Lines file."""
    if not os.path.exists(chores_file):
        return []
    
    chores = []
    with open(chores_file, 'r') as f:
        for line in f:
            if line.strip():
                chores.append(json.loads(line))
    return chores

def format_status_short(status):
    """Convert status to short form for display."""
    status_map = {
        'design': 'DSN',
        'design_review': 'D-R',
        'design_ready': 'D-OK',
        'plan': 'PLN',
        'plan_review': 'P-R',
        'plan_ready': 'P-OK',
        'work': 'WRK',
        'work_review': 'W-R'
    }
    return status_map.get(status, status[:3].upper())

def get_chore_summary():
    """Get summary of active chores for TMUX display."""
    chores_file = os.path.expanduser("~/SkipsChoreData/chores.jsonl")
    chores = load_active_chores(chores_file)
    
    if not chores:
        return "No active chores"
    
    # Count by status
    status_counts = {}
    for chore in chores:
        status = chore['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Format for display
    parts = []
    for status, count in status_counts.items():
        short_status = format_status_short(status)
        parts.append(f"{short_status}:{count}")
    
    return f"Chores[{' '.join(parts)}]"

def get_current_chore():
    """Get details of first active chore."""
    chores_file = os.path.expanduser("~/SkipsChoreData/chores.jsonl")
    chores = load_active_chores(chores_file)
    
    if not chores:
        return "No active chores"
    
    chore = chores[0]
    name = chore['name'][:20] + "..." if len(chore['name']) > 20 else chore['name']
    status = format_status_short(chore['status'])
    
    return f"{name} [{status}]"

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--current":
        print(get_current_chore())
    else:
        print(get_chore_summary())
