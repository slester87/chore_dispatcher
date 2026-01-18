#!/usr/bin/env python3

from fastmcp import FastMCP
from chore import Chore, ChoreStatus
from chore_repository import ChoreRepository
from typing import Optional, List

# Initialize MCP server and repository
mcp = FastMCP("chore-dispatcher")
repo = ChoreRepository("/Users/skippo/Development/SkipsChoreData/chores.jsonl")

@mcp.tool()
def create_chore(name: str, description: str = "") -> dict:
    """Create a new chore with the given name and description."""
    chore = repo.create(name, description)
    return {
        "id": chore.id,
        "name": chore.name,
        "description": chore.description,
        "status": chore.status.value
    }

@mcp.tool()
def get_chore(chore_id: int) -> Optional[dict]:
    """Get a chore by its ID."""
    chore = repo.read(chore_id)
    if not chore:
        return None

    return {
        "id": chore.id,
        "name": chore.name,
        "description": chore.description,
        "status": chore.status.value,
        "next_chore_id": chore.next_chore.id if chore.next_chore else None,
        "progress_info": chore.progress_info,
        "review_info": chore.review_info
    }

@mcp.tool()
def update_chore(chore_id: int, name: Optional[str] = None,
                description: Optional[str] = None, status: Optional[str] = None) -> Optional[dict]:
    """Update a chore's properties."""
    status_enum = None
    if status:
        try:
            status_enum = ChoreStatus(status)
        except ValueError:
            return {"error": f"Invalid status: {status}"}

    chore = repo.update(chore_id, name=name, description=description, status=status_enum)
    if not chore:
        return None

    return {
        "id": chore.id,
        "name": chore.name,
        "description": chore.description,
        "status": chore.status.value
    }

@mcp.tool()
def worker_update_progress(chore_id: int, progress_info: str) -> Optional[dict]:
    """Worker agent updates progress info for design, plan, and work states."""
    chore = repo.read(chore_id)
    if not chore:
        return {"error": "Chore not found"}
    
    # Worker can only update progress for these states
    worker_states = [ChoreStatus.DESIGN, ChoreStatus.PLAN, ChoreStatus.WORK]
    if chore.status not in worker_states:
        return {"error": f"Worker cannot update chore in {chore.status.value} state"}
    
    updated_chore = repo.update(chore_id, progress_info=progress_info)
    if not updated_chore:
        return {"error": "Failed to update progress"}
    
    return {
        "id": updated_chore.id,
        "status": updated_chore.status.value,
        "progress_info": updated_chore.progress_info,
        "message": "Progress updated by worker"
    }

@mcp.tool()
def reviewer_update_feedback(chore_id: int, review_info: str) -> Optional[dict]:
    """Reviewer agent updates review info for design_review, plan_review, and work_review states."""
    chore = repo.read(chore_id)
    if not chore:
        return {"error": "Chore not found"}
    
    # Reviewer can only update feedback for these states
    reviewer_states = [ChoreStatus.DESIGN_REVIEW, ChoreStatus.PLAN_REVIEW, ChoreStatus.WORK_REVIEW]
    if chore.status not in reviewer_states:
        return {"error": f"Reviewer cannot update chore in {chore.status.value} state"}
    
    updated_chore = repo.update(chore_id, review_info=review_info)
    if not updated_chore:
        return {"error": "Failed to update review"}
    
    return {
        "id": updated_chore.id,
        "status": updated_chore.status.value,
        "review_info": updated_chore.review_info,
        "message": "Review updated by reviewer"
    }

@mcp.tool()
def worker_advance_to_review(chore_id: int, progress_info: str) -> Optional[dict]:
    """Worker completes work phase and advances to review with progress info."""
    chore = repo.read(chore_id)
    if not chore:
        return {"error": "Chore not found"}
    
    # Map work states to their review states
    work_to_review = {
        ChoreStatus.DESIGN: ChoreStatus.DESIGN_REVIEW,
        ChoreStatus.PLAN: ChoreStatus.PLAN_REVIEW,
        ChoreStatus.WORK: ChoreStatus.WORK_REVIEW
    }
    
    if chore.status not in work_to_review:
        return {"error": f"Cannot advance from {chore.status.value} to review"}
    
    next_status = work_to_review[chore.status]
    updated_chore = repo.update(chore_id, status=next_status, progress_info=progress_info)
    
    if not updated_chore:
        return {"error": "Failed to advance to review"}
    
    return {
        "id": updated_chore.id,
        "status": updated_chore.status.value,
        "progress_info": updated_chore.progress_info,
        "advanced": True,
        "message": f"Worker advanced chore to {next_status.value}"
    }

@mcp.tool()
def reviewer_approve_or_reject(chore_id: int, approved: bool, review_info: str) -> Optional[dict]:
    """Reviewer approves (advances to ready) or rejects (sends back to work) with review feedback."""
    chore = repo.read(chore_id)
    if not chore:
        return {"error": "Chore not found"}
    
    # Map review states to ready/work states
    review_transitions = {
        ChoreStatus.DESIGN_REVIEW: {
            "approve": ChoreStatus.DESIGN_READY,
            "reject": ChoreStatus.DESIGN
        },
        ChoreStatus.PLAN_REVIEW: {
            "approve": ChoreStatus.PLAN_READY,
            "reject": ChoreStatus.PLAN
        },
        ChoreStatus.WORK_REVIEW: {
            "approve": ChoreStatus.WORK_DONE,
            "reject": ChoreStatus.WORK
        }
    }
    
    if chore.status not in review_transitions:
        return {"error": f"Cannot review chore in {chore.status.value} state"}
    
    next_status = review_transitions[chore.status]["approve" if approved else "reject"]
    updated_chore = repo.update(chore_id, status=next_status, review_info=review_info)
    
    if not updated_chore:
        return {"error": "Failed to update review decision"}
    
    action = "approved" if approved else "rejected"
    return {
        "id": updated_chore.id,
        "status": updated_chore.status.value,
        "review_info": updated_chore.review_info,
        "action": action,
        "message": f"Reviewer {action} chore, moved to {next_status.value}"
    }

@mcp.tool()
def delete_chore(chore_id: int) -> dict:
    """Delete a chore by its ID."""
    success = repo.delete(chore_id)
    return {"deleted": success}

@mcp.tool()
def list_chores() -> List[dict]:
    """List all chores."""
    chores = repo.list_all()
    return [
        {
            "id": chore.id,
            "name": chore.name,
            "description": chore.description,
            "status": chore.status.value
        }
        for chore in chores
    ]

@mcp.tool()
def find_chores_by_status(status: str) -> List[dict]:
    """Find chores by their status."""
    try:
        status_enum = ChoreStatus(status)
    except ValueError:
        return []

    chores = repo.find_by_status(status_enum)
    return [
        {
            "id": chore.id,
            "name": chore.name,
            "description": chore.description,
            "status": chore.status.value
        }
        for chore in chores
    ]

@mcp.tool()
def advance_chore_status(chore_id: int) -> Optional[dict]:
    """Advance a chore to the next status in the workflow."""
    chore = repo.read(chore_id)
    if not chore:
        return None

    # Get the next status
    current_status = chore.status
    next_status = None

    status_order = [
        ChoreStatus.DESIGN, ChoreStatus.DESIGN_REVIEW, ChoreStatus.DESIGN_READY,
        ChoreStatus.PLAN, ChoreStatus.PLAN_REVIEW, ChoreStatus.PLAN_READY,
        ChoreStatus.WORK, ChoreStatus.WORK_REVIEW, ChoreStatus.WORK_DONE
    ]

    try:
        current_index = status_order.index(current_status)
        if current_index < len(status_order) - 1:
            next_status = status_order[current_index + 1]
        else:
            return {"id": chore.id, "name": chore.name, "status": chore.status.value, "advanced": False, "message": "Already at final status"}
    except ValueError:
        return {"error": "Invalid current status"}

    # Use repository update to trigger lifecycle management
    updated_chore = repo.update(chore_id, status=next_status)
    if not updated_chore:
        return {"error": "Failed to update chore"}

    return {
        "id": updated_chore.id,
        "name": updated_chore.name,
        "status": updated_chore.status.value,
        "advanced": True
    }

@mcp.tool()
def get_worker_chores() -> List[dict]:
    """Get chores that worker agent should work on (design, plan, work states)."""
    worker_states = [ChoreStatus.DESIGN, ChoreStatus.PLAN, ChoreStatus.WORK]
    worker_chores = []
    
    for status in worker_states:
        chores = repo.find_by_status(status)
        worker_chores.extend(chores)
    
    return [
        {
            "id": chore.id,
            "name": chore.name,
            "description": chore.description,
            "status": chore.status.value,
            "progress_info": chore.progress_info,
            "review_info": chore.review_info
        }
        for chore in worker_chores
    ]

@mcp.tool()
def get_reviewer_chores() -> List[dict]:
    """Get chores that reviewer agent should work on (design_review, plan_review, work_review states)."""
    reviewer_states = [ChoreStatus.DESIGN_REVIEW, ChoreStatus.PLAN_REVIEW, ChoreStatus.WORK_REVIEW]
    reviewer_chores = []
    
    for status in reviewer_states:
        chores = repo.find_by_status(status)
        reviewer_chores.extend(chores)
    
    return [
        {
            "id": chore.id,
            "name": chore.name,
            "description": chore.description,
            "status": chore.status.value,
            "progress_info": chore.progress_info,
            "review_info": chore.review_info
        }
        for chore in reviewer_chores
    ]

@mcp.tool()
def get_chore_statuses() -> List[str]:
    """Get all possible chore statuses."""
    return [status.value for status in ChoreStatus]

@mcp.tool()
def list_archived_chores() -> dict:
    """List archived/completed chores from the archive file."""
    import json
    import os

    archive_file = "/Users/skippo/Development/SkipsChoreData/chores_completed.jsonl"

    if not os.path.exists(archive_file):
        return {"archived_chores": [], "message": "No archive file found"}

    archived_chores = []
    try:
        with open(archive_file, 'r') as f:
            for line in f:
                if line.strip():
                    chore_data = json.loads(line)
                    archived_chores.append(chore_data)
    except Exception as e:
        return {"error": f"Failed to read archive: {str(e)}"}

    return {"archived_chores": archived_chores, "count": len(archived_chores)}

if __name__ == "__main__":
    mcp.run()
