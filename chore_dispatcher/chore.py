from enum import Enum
from typing import Optional
from chore_src.snowflake import Snowflake


class ChoreStatus(Enum):
    DESIGN = "design"
    DESIGN_REVIEW = "design_review"
    PLAN = "plan"
    PLAN_REVIEW = "plan_review"
    WORK = "work"
    WORK_REVIEW = "work_review"


class Chore:
    _snowflake = Snowflake(node_id=1)  # Class-level snowflake generator
    
    def __init__(self, name: str, description: str = ""):
        self.id = self._snowflake.next_id()
        self.name = name
        self.description = description
        self.status = ChoreStatus.DESIGN
        self.next_chore: Optional['Chore'] = None
    
    def set_next_chore(self, chore: 'Chore') -> None:
        self.next_chore = chore
    
    def advance_status(self) -> bool:
        """Advance to next status. Returns True if advanced, False if already complete."""
        statuses = list(ChoreStatus)
        current_index = statuses.index(self.status)
        
        if current_index < len(statuses) - 1:
            self.status = statuses[current_index + 1]
            return True
        return False
    
    def is_complete(self) -> bool:
        return self.status == ChoreStatus.WORK_REVIEW
    
    def get_next_chore(self) -> Optional['Chore']:
        """Returns next chore if this one is complete, None otherwise."""
        return self.next_chore if self.is_complete() else None
    
    def __str__(self) -> str:
        return f"Chore({self.id}, '{self.name}', {self.status.value})"
