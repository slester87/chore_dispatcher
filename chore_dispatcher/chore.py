from enum import Enum
from typing import Optional, List
from chore_src.snowflake import Snowflake


class ChoreStatus(Enum):
    DESIGN = "design"
    DESIGN_REVIEW = "design_review"
    DESIGN_READY = "design_ready"
    PLAN = "plan"
    PLAN_REVIEW = "plan_review"
    PLAN_READY = "plan_ready"
    WORK = "work"
    WORK_REVIEW = "work_review"
    WORK_DONE = "work_done"


class Chore:
    _snowflake = Snowflake(node_id=1)  # Class-level snowflake generator
    
    def __init__(self, name: str, description: str = "", parent_chore_id: Optional[int] = None):
        self.id = self._snowflake.next_id()
        self.name = name
        self.description = description
        self.status = ChoreStatus.DESIGN
        self.next_chore: Optional['Chore'] = None
        self.progress_info: Optional[str] = None
        self.review_info: Optional[str] = None
        self.parent_chore_id = parent_chore_id
        self.sub_chores: List['Chore'] = []
    
    def add_sub_chore(self, sub_chore: 'Chore') -> None:
        """Add a sub-chore to this chore."""
        sub_chore.parent_chore_id = self.id
        self.sub_chores.append(sub_chore)
    
    def get_sub_chores(self) -> List['Chore']:
        """Get all sub-chores of this chore."""
        return self.sub_chores.copy()
    
    @property
    def is_parent(self) -> bool:
        """Check if this chore has sub-chores."""
        return len(self.sub_chores) > 0
    
    @property
    def is_sub_chore(self) -> bool:
        """Check if this chore is a sub-chore."""
        return self.parent_chore_id is not None
    
    def can_advance(self) -> bool:
        """Check if chore can advance status (all sub-chores must be complete)."""
        if not self.is_parent:
            return True
        return all(sub_chore.is_complete() for sub_chore in self.sub_chores)
    
    def set_next_chore(self, chore: 'Chore') -> None:
        self.next_chore = chore
    
    def advance_status(self) -> bool:
        """Advance to next status. Returns True if advanced, False if already complete."""
        if not self.can_advance():
            return False
            
        statuses = list(ChoreStatus)
        current_index = statuses.index(self.status)
        
        if current_index < len(statuses) - 1:
            self.status = statuses[current_index + 1]
            return True
        return False
    
    def is_complete(self) -> bool:
        return self.status == ChoreStatus.WORK_DONE
    
    def get_next_chore(self) -> Optional['Chore']:
        """Returns next chore if this one is complete, None otherwise."""
        return self.next_chore if self.is_complete() else None
    
    def __str__(self) -> str:
        return f"Chore({self.id}, '{self.name}', {self.status.value})"
