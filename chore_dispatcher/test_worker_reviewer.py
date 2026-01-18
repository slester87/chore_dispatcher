#!/usr/bin/env python3
"""
Test script for worker/reviewer agent separation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chore_repository import ChoreRepository
from chore import ChoreStatus

def test_worker_reviewer_workflow():
    """Test the complete worker/reviewer workflow"""
    
    # Initialize repository
    repo = ChoreRepository("/tmp/test_chores.jsonl")
    
    # Create a test chore
    chore = repo.create("Test Worker/Reviewer Flow", "Testing the new workflow")
    print(f"Created chore: {chore.id} - {chore.name} ({chore.status.value})")
    
    # Worker updates progress in design phase
    updated = repo.update(chore.id, progress_info="Worker: Initial design concepts drafted")
    print(f"Worker progress update: {updated.progress_info}")
    
    # Worker advances to design_review
    updated = repo.update(chore.id, status=ChoreStatus.DESIGN_REVIEW, 
                         progress_info="Worker: Design complete, ready for review")
    print(f"Advanced to review: {updated.status.value}")
    
    # Reviewer provides feedback
    updated = repo.update(chore.id, review_info="Reviewer: Design looks good, minor adjustments needed")
    print(f"Reviewer feedback: {updated.review_info}")
    
    # Reviewer approves (advances to design_ready)
    updated = repo.update(chore.id, status=ChoreStatus.DESIGN_READY,
                         review_info="Reviewer: Approved - proceed to planning")
    print(f"Reviewer approved: {updated.status.value}")
    
    # Worker starts planning
    updated = repo.update(chore.id, status=ChoreStatus.PLAN,
                         progress_info="Worker: Starting implementation plan")
    print(f"Worker planning: {updated.status.value}")
    
    # Display final state
    final_chore = repo.read(chore.id)
    print(f"\nFinal state:")
    print(f"  Status: {final_chore.status.value}")
    print(f"  Progress: {final_chore.progress_info}")
    print(f"  Review: {final_chore.review_info}")
    
    # Clean up
    os.remove("/tmp/test_chores.jsonl")
    if os.path.exists("/tmp/test_chores_completed.jsonl"):
        os.remove("/tmp/test_chores_completed.jsonl")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_worker_reviewer_workflow()
