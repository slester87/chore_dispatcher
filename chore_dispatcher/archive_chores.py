#!/usr/bin/env python3
"""
Chore Archive Script - Move completed chores to chores_completed.jsonl
"""

import sys
import os
import json
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chore_repository import ChoreRepository
from chore import ChoreStatus


def archive_completed_chores(data_path: str = None) -> int:
    """Archive all completed chores to chores_completed.jsonl."""
    data_path = data_path or os.path.expanduser("~/SkipsChoreData/chores.jsonl")
    completed_path = data_path.replace('.jsonl', '_completed.jsonl')
    
    repo = ChoreRepository(data_path)
    
    # Find all completed chores
    completed_chores = repo.find_by_status(ChoreStatus.WORK_DONE)
    
    if not completed_chores:
        print("No completed chores to archive")
        return 0
    
    print(f"Found {len(completed_chores)} completed chores to archive:")
    
    archived_count = 0
    for chore in completed_chores:
        print(f"  📦 {chore.id}: {chore.name}")
        
        try:
            # Append to completed file
            chore_data = {
                'id': chore.id,
                'name': chore.name,
                'description': chore.description,
                'status': chore.status.value,
                'next_chore_id': chore.next_chore.id if chore.next_chore else None
            }
            
            with open(completed_path, 'a') as f:
                f.write(json.dumps(chore_data) + '\n')
            
            # Remove from active chores
            repo.delete(chore.id)
            archived_count += 1
            
        except Exception as e:
            print(f"    ❌ Failed to archive {chore.id}: {e}")
    
    print(f"\n✅ Archived {archived_count} chores to {completed_path}")
    
    # Show remaining active chores
    remaining = repo.list_all()
    if remaining:
        print(f"\n📋 {len(remaining)} active chores remaining:")
        for chore in remaining:
            print(f"  • {chore.id}: {chore.status.value.upper()} - {chore.name}")
    else:
        print("\n🎉 No active chores remaining - clean slate!")
    
    return archived_count


def main():
    """Main archive function."""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Usage: python3 archive_chores.py [data_path]")
        print("Archive all completed (WORK_DONE) chores to chores_completed.jsonl")
        return 0
    
    data_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        archived_count = archive_completed_chores(data_path)
        return 0 if archived_count >= 0 else 1
    except Exception as e:
        print(f"❌ Archive failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
