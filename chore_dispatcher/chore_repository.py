from typing import Dict, List, Optional
import json
import os
from chore import Chore, ChoreStatus


class ChoreRepository:
    def __init__(self, storage_file: str = "chores.jsonl"):
        self.storage_file = storage_file
        self.completed_file = storage_file.replace('.jsonl', '_completed.jsonl') if storage_file.endswith('.jsonl') else storage_file + '_completed'
        self._chores: Dict[int, Chore] = {}
        self._load_from_file()
    
    def _load_from_file(self):
        """Load chores from JSONL file."""
        if not os.path.exists(self.storage_file):
            return
        
        with open(self.storage_file, 'r') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    chore = self._dict_to_chore(data)
                    self._chores[chore.id] = chore
    
    def _save_to_file(self):
        """Save all chores to JSONL file."""
        with open(self.storage_file, 'w') as f:
            for chore in self._chores.values():
                f.write(json.dumps(self._chore_to_dict(chore)) + '\n')
    
    def _archive_completed_chore(self, chore: Chore):
        """Move completed chore to historical archive."""
        with open(self.completed_file, 'a') as f:
            f.write(json.dumps(self._chore_to_dict(chore)) + '\n')
    
    def _chore_to_dict(self, chore: Chore) -> dict:
        """Convert chore to dictionary."""
        return {
            'id': chore.id,
            'name': chore.name,
            'description': chore.description,
            'status': chore.status.value,
            'next_chore_id': chore.next_chore.id if chore.next_chore else None,
            'progress_info': chore.progress_info,
            'review_info': chore.review_info
        }
    
    def _dict_to_chore(self, data: dict) -> Chore:
        """Convert dictionary to chore."""
        chore = Chore.__new__(Chore)  # Create without calling __init__
        chore.id = data['id']
        chore.name = data['name']
        chore.description = data['description']
        chore.status = ChoreStatus(data['status'])
        chore.next_chore = None  # Will be linked after all chores loaded
        chore.progress_info = data.get('progress_info')
        chore.review_info = data.get('review_info')
        return chore
    
    def create(self, name: str, description: str = "") -> Chore:
        """Create a new chore."""
        chore = Chore(name, description)
        self._chores[chore.id] = chore
        self._save_to_file()
        return chore
    
    def read(self, chore_id: int) -> Optional[Chore]:
        """Read a chore by ID."""
        return self._chores.get(chore_id)
    
    def update(self, chore_id: int, name: str = None, description: str = None, 
               status: ChoreStatus = None, progress_info: str = None, 
               review_info: str = None) -> Optional[Chore]:
        """Update a chore's properties."""
        chore = self._chores.get(chore_id)
        if not chore:
            return None
        
        old_status = chore.status
        
        if name is not None:
            chore.name = name
        if description is not None:
            chore.description = description
        if status is not None:
            chore.status = status
        if progress_info is not None:
            chore.progress_info = progress_info
        if review_info is not None:
            chore.review_info = review_info
        
        # If chore became complete, archive it and remove from active
        if old_status != ChoreStatus.WORK_DONE and chore.status == ChoreStatus.WORK_DONE:
            self._archive_completed_chore(chore)
            del self._chores[chore_id]
        
        self._save_to_file()
        return chore
    
    def delete(self, chore_id: int) -> bool:
        """Delete a chore by ID."""
        if chore_id in self._chores:
            del self._chores[chore_id]
            self._save_to_file()
            return True
        return False
    
    def list_all(self) -> List[Chore]:
        """List all chores."""
        return list(self._chores.values())
    
    def find_by_status(self, status: ChoreStatus) -> List[Chore]:
        """Find chores by status."""
        return [chore for chore in self._chores.values() if chore.status == status]
