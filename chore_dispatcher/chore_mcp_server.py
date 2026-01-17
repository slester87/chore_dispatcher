#!/usr/bin/env python3

from fastmcp import FastMCP
from chore import Chore, ChoreStatus
from chore_repository import ChoreRepository
from typing import Optional, List

# Initialize MCP server and repository
mcp = FastMCP("Chore Manager")
repo = ChoreRepository("/Users/skippo/SkipsChoreData/chores.jsonl")

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
        "next_chore_id": chore.next_chore.id if chore.next_chore else None
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
    
    advanced = chore.advance_status()
    if advanced:
        repo.update(chore_id, status=chore.status)
    
    return {
        "id": chore.id,
        "name": chore.name,
        "status": chore.status.value,
        "advanced": advanced
    }

@mcp.tool()
def get_chore_statuses() -> List[str]:
    """Get all possible chore statuses."""
    return [status.value for status in ChoreStatus]

if __name__ == "__main__":
    mcp.run()
