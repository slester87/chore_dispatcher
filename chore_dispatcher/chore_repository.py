from typing import Dict, List, Optional
import json
import os
from chore import Chore, ChoreStatus
from chore_lifecycle_manager import create_lifecycle_manager
from dispatcher_hooks import get_dispatcher_hooks


class ChoreRepository:
    def __init__(self, storage_file: str = "/Users/skippo/Development/SkipsChoreData/chores.jsonl"):
        self.storage_file = storage_file
        self.completed_file = storage_file.replace('.jsonl', '_completed.jsonl') if storage_file.endswith('.jsonl') else storage_file + '_completed'
        self._chores: Dict[int, Chore] = {}
        self.lifecycle_manager = create_lifecycle_manager(storage_file, self.completed_file)
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
        
        # Link chore chains and parent-child relationships
        self._link_chore_chains()
        self._link_parent_child_relationships()
    
    def _link_parent_child_relationships(self):
        """Link parent-child relationships based on parent_chore_id references."""
        for chore in self._chores.values():
            if chore.parent_chore_id:
                parent_chore = self._chores.get(chore.parent_chore_id)
                if parent_chore:
                    parent_chore.sub_chores.append(chore)
    
    def _link_chore_chains(self):
        """Link chores based on next_chore_id references"""
        for chore in self._chores.values():
            if hasattr(chore, '_next_chore_id') and chore._next_chore_id:
                next_chore = self._chores.get(chore._next_chore_id)
                if next_chore:
                    chore.next_chore = next_chore
    
    def _save_to_file(self):
        """Save all chores to JSONL file using lifecycle manager."""
        self.lifecycle_manager.archival_manager.save_active_chores(self._chores)
    
    def _archive_completed_chore(self, chore: Chore):
        """Archive completed chore using lifecycle manager."""
        self.lifecycle_manager.archival_manager.archive_completed_chore(chore)
    
    def _chore_to_dict(self, chore: Chore) -> dict:
        """Convert chore to dictionary."""
        return {
            'id': chore.id,
            'name': chore.name,
            'description': chore.description,
            'status': chore.status.value,
            'next_chore_id': chore.next_chore.id if chore.next_chore else None,
            'progress_info': chore.progress_info,
            'review_info': chore.review_info,
            'parent_chore_id': chore.parent_chore_id
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
        chore.parent_chore_id = data.get('parent_chore_id')
        chore.sub_chores = []  # Will be populated after all chores loaded
        # Store next_chore_id for linking
        chore._next_chore_id = data.get('next_chore_id')
        return chore
    
    def create_sub_chore(self, parent_id: int, name: str, description: str = "") -> Optional[Chore]:
        """Create a sub-chore under a parent chore."""
        parent_chore = self._chores.get(parent_id)
        if not parent_chore:
            return None
            
        sub_chore = Chore(name, description, parent_chore_id=parent_id)
        parent_chore.add_sub_chore(sub_chore)
        self._chores[sub_chore.id] = sub_chore
        self._save_to_file()
        
        # Notify dispatcher hooks
        try:
            get_dispatcher_hooks().on_chore_created(sub_chore)
        except Exception as e:
            print(f"Dispatcher hook failed: {e}")
            
        return sub_chore
    
    def get_sub_chores(self, parent_id: int) -> List[Chore]:
        """Get all sub-chores of a parent chore."""
        parent_chore = self._chores.get(parent_id)
        if not parent_chore:
            return []
        return parent_chore.get_sub_chores()
    
    def get_parent_chore(self, chore_id: int) -> Optional[Chore]:
        """Get the parent chore of a sub-chore."""
        chore = self._chores.get(chore_id)
        if not chore or not chore.is_sub_chore:
            return None
        return self._chores.get(chore.parent_chore_id)
    
    def find_by_parent_id(self, parent_id: int) -> List[Chore]:
        """Find all chores with the given parent ID."""
        return [chore for chore in self._chores.values() if chore.parent_chore_id == parent_id]
    
    def find_root_chores(self) -> List[Chore]:
        """Find all chores with no parent (root chores)."""
        return [chore for chore in self._chores.values() if not chore.is_sub_chore]

    def create(self, name: str, description: str = "") -> Chore:
        """Create a new chore."""
        chore = Chore(name, description)
        self._chores[chore.id] = chore
        self._save_to_file()
        
        # Notify dispatcher hooks
        try:
            get_dispatcher_hooks().on_chore_created(chore)
        except Exception as e:
            print(f"Dispatcher hook failed: {e}")
            
        return chore
    
    def read(self, chore_id: int) -> Optional[Chore]:
        """Read a chore by ID."""
        return self._chores.get(chore_id)
    
    def update(self, chore_id: int, name: str = None, description: str = None, 
               status: ChoreStatus = None, progress_info: str = None, 
               review_info: str = None) -> Optional[Chore]:
        """Update a chore's properties using lifecycle manager."""
        chore = self._chores.get(chore_id)
        if not chore:
            return None
        
        old_status = chore.status
        
        # Update properties
        if name is not None:
            chore.name = name
        if description is not None:
            chore.description = description
        if progress_info is not None:
            chore.progress_info = progress_info
        if review_info is not None:
            chore.review_info = review_info
        
        # Handle status transitions through lifecycle manager
        if status is not None and status != old_status:
            try:
                result = self.lifecycle_manager.transition_chore_state(
                    chore, status, self._chores, progress_info, review_info
                )
                
                # Handle chain activation
                if result.get('chain_activation', {}).get('next_chore_activated'):
                    chain_info = result['chain_activation']
                    print(f"Chain activated: {chain_info['activation_details']}")
                
                # Notify dispatcher hooks of state change
                try:
                    get_dispatcher_hooks().on_chore_state_change(chore, old_status, status)
                except Exception as e:
                    print(f"Dispatcher hook failed: {e}")
                
                # If chore was completed and archived, remove from memory
                if status == ChoreStatus.WORK_DONE:
                    # Archive and remove from active chores
                    if chore_id in self._chores:
                        del self._chores[chore_id]
                    return None  # Chore is now archived
                
            except Exception as e:
                print(f"Lifecycle transition failed for chore {chore_id}: {e}")
                # Fallback to old behavior
                chore.status = status
                self._save_to_file()
        else:
            # No status change, just save
            self._save_to_file()
        
        return chore
    
    def delete(self, chore_id: int) -> bool:
        """Delete a chore by ID. Also deletes all sub-chores."""
        if chore_id not in self._chores:
            return False
            
        chore = self._chores[chore_id]
        
        # Delete all sub-chores first
        for sub_chore in chore.get_sub_chores():
            self.delete(sub_chore.id)
        
        # Remove from parent's sub_chores list if this is a sub-chore
        if chore.is_sub_chore:
            parent_chore = self._chores.get(chore.parent_chore_id)
            if parent_chore:
                parent_chore.sub_chores = [sc for sc in parent_chore.sub_chores if sc.id != chore_id]
        
        # Notify dispatcher hooks before deletion
        try:
            get_dispatcher_hooks().on_chore_deleted(chore_id)
        except Exception as e:
            print(f"Dispatcher hook failed: {e}")
            
        del self._chores[chore_id]
        self._save_to_file()
        return True
    
    def list_all(self) -> List[Chore]:
        """List all chores."""
        return list(self._chores.values())
    
    def find_by_status(self, status: ChoreStatus) -> List[Chore]:
        """Find chores by status."""
        return [chore for chore in self._chores.values() if chore.status == status]
    
    def validate_system_integrity(self) -> Dict:
        """Validate system integrity using lifecycle manager."""
        return self.lifecycle_manager.validate_system_integrity()
    
    def repair_system(self) -> Dict:
        """Repair system inconsistencies using lifecycle manager."""
        repair_result = self.lifecycle_manager.repair_system()
        
        # Reload chores after repair
        self._chores.clear()
        self._load_from_file()
        
        return repair_result
    
    def validate_chains(self) -> Dict:
        """Validate chore chain integrity."""
        return self.lifecycle_manager.validate_chain_integrity(self._chores)
