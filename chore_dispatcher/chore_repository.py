from typing import Dict, List, Optional
from chore import Chore, ChoreStatus


class ChoreRepository:
    def __init__(self):
        self._chores: Dict[int, Chore] = {}
    
    def create(self, name: str, description: str = "") -> Chore:
        """Create a new chore."""
        chore = Chore(name, description)
        self._chores[chore.id] = chore
        return chore
    
    def read(self, chore_id: int) -> Optional[Chore]:
        """Read a chore by ID."""
        return self._chores.get(chore_id)
    
    def update(self, chore_id: int, name: str = None, description: str = None, 
               status: ChoreStatus = None) -> Optional[Chore]:
        """Update a chore's properties."""
        chore = self._chores.get(chore_id)
        if not chore:
            return None
        
        if name is not None:
            chore.name = name
        if description is not None:
            chore.description = description
        if status is not None:
            chore.status = status
        
        return chore
    
    def delete(self, chore_id: int) -> bool:
        """Delete a chore by ID."""
        if chore_id in self._chores:
            del self._chores[chore_id]
            return True
        return False
    
    def list_all(self) -> List[Chore]:
        """List all chores."""
        return list(self._chores.values())
    
    def find_by_status(self, status: ChoreStatus) -> List[Chore]:
        """Find chores by status."""
        return [chore for chore in self._chores.values() if chore.status == status]
