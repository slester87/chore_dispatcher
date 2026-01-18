#!/usr/bin/env python3
"""
Test the new worker/reviewer MCP tools directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chore_repository import ChoreRepository
from chore import ChoreStatus

def test_mcp_workflow():
    """Test the MCP workflow functions directly"""
    
    # Initialize repository
    repo = ChoreRepository("/tmp/test_mcp_chores.jsonl")
    
    # Create a test chore
    chore = repo.create("Test MCP Workflow", "Testing worker/reviewer MCP tools")
    chore_id = chore.id
    print(f"Created chore: {chore_id}")
    
    # Test worker states validation
    worker_states = [ChoreStatus.DESIGN, ChoreStatus.PLAN, ChoreStatus.WORK]
    reviewer_states = [ChoreStatus.DESIGN_REVIEW, ChoreStatus.PLAN_REVIEW, ChoreStatus.WORK_REVIEW]
    
    print(f"Current status: {chore.status.value}")
    print(f"Worker can work on: {chore.status in worker_states}")
    print(f"Reviewer can work on: {chore.status in reviewer_states}")
    
    # Simulate worker update progress
    if chore.status in worker_states:
        updated = repo.update(chore_id, progress_info="Worker: Design phase started")
        print(f"Worker progress: {updated.progress_info}")
    
    # Simulate worker advance to review
    work_to_review = {
        ChoreStatus.DESIGN: ChoreStatus.DESIGN_REVIEW,
        ChoreStatus.PLAN: ChoreStatus.PLAN_REVIEW,
        ChoreStatus.WORK: ChoreStatus.WORK_REVIEW
    }
    
    if chore.status in work_to_review:
        next_status = work_to_review[chore.status]
        updated = repo.update(chore_id, status=next_status, progress_info="Worker: Ready for review")
        print(f"Advanced to: {updated.status.value}")
        
        # Now test reviewer functionality
        if updated.status in reviewer_states:
            reviewed = repo.update(chore_id, review_info="Reviewer: Looks good!")
            print(f"Reviewer feedback: {reviewed.review_info}")
            
            # Test approval
            review_to_ready = {
                ChoreStatus.DESIGN_REVIEW: ChoreStatus.DESIGN_READY,
                ChoreStatus.PLAN_REVIEW: ChoreStatus.PLAN_READY,
                ChoreStatus.WORK_REVIEW: ChoreStatus.WORK_DONE
            }
            
            ready_status = review_to_ready[updated.status]
            approved = repo.update(chore_id, status=ready_status, review_info="Reviewer: Approved!")
            print(f"Approved to: {approved.status.value}")
    
    # Clean up
    os.remove("/tmp/test_mcp_chores.jsonl")
    if os.path.exists("/tmp/test_mcp_chores_completed.jsonl"):
        os.remove("/tmp/test_mcp_chores_completed.jsonl")
    
    print("MCP workflow test completed!")

if __name__ == "__main__":
    test_mcp_workflow()
