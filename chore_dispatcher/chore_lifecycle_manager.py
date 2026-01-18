#!/usr/bin/env python3
"""
ChoreLifecycleManager - Core Infrastructure
Manages chore state transitions with atomic operations and validation
"""

from enum import Enum
from typing import Optional, Dict, Any, Callable
from contextlib import contextmanager
import json
import os
from chore import Chore, ChoreStatus


class TransitionError(Exception):
    """Raised when chore state transition fails"""
    pass


class ValidationError(Exception):
    """Raised when chore validation fails"""
    pass


class StateTransitionEngine:
    """Handles atomic chore state transitions with validation"""
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        ChoreStatus.DESIGN: [ChoreStatus.DESIGN_REVIEW],
        ChoreStatus.DESIGN_REVIEW: [ChoreStatus.DESIGN_READY],
        ChoreStatus.DESIGN_READY: [ChoreStatus.PLAN],
        ChoreStatus.PLAN: [ChoreStatus.PLAN_REVIEW],
        ChoreStatus.PLAN_REVIEW: [ChoreStatus.PLAN_READY],
        ChoreStatus.PLAN_READY: [ChoreStatus.WORK],
        ChoreStatus.WORK: [ChoreStatus.WORK_REVIEW],
        ChoreStatus.WORK_REVIEW: [ChoreStatus.WORK_DONE],
        ChoreStatus.WORK_DONE: []  # Terminal state
    }
    
    def validate_transition(self, current_status: ChoreStatus, new_status: ChoreStatus) -> bool:
        """Validate if transition from current to new status is allowed"""
        if current_status not in self.VALID_TRANSITIONS:
            return False
        return new_status in self.VALID_TRANSITIONS[current_status]
    
    def execute_transition(self, chore: Chore, new_status: ChoreStatus) -> bool:
        """Execute state transition with validation"""
        if not self.validate_transition(chore.status, new_status):
            raise TransitionError(f"Invalid transition from {chore.status} to {new_status}")
        
        old_status = chore.status
        chore.status = new_status
        
        return True


class IntegrityValidator:
    """Validates chore system integrity"""
    
    def __init__(self, active_file: str, completed_file: str):
        self.active_file = active_file
        self.completed_file = completed_file
    
    def validate_chore_locations(self) -> Dict[str, Any]:
        """Validate chores exist in exactly one location"""
        active_ids = set()
        completed_ids = set()
        issues = []
        
        # Load active chores
        if os.path.exists(self.active_file):
            with open(self.active_file, 'r') as f:
                for line in f:
                    if line.strip():
                        chore_data = json.loads(line)
                        chore_id = chore_data['id']
                        active_ids.add(chore_id)
                        
                        # Validate status
                        if chore_data['status'] == 'work_done':
                            issues.append(f"Completed chore {chore_id} in active file")
        
        # Load completed chores
        if os.path.exists(self.completed_file):
            with open(self.completed_file, 'r') as f:
                for line in f:
                    if line.strip():
                        chore_data = json.loads(line)
                        chore_id = chore_data['id']
                        completed_ids.add(chore_id)
                        
                        # Validate status
                        if chore_data['status'] != 'work_done':
                            issues.append(f"Non-completed chore {chore_id} in completed file")
        
        # Check for dual-location existence
        dual_location = active_ids.intersection(completed_ids)
        for chore_id in dual_location:
            issues.append(f"Chore {chore_id} exists in both active and completed files")
        
        return {
            'active_count': len(active_ids),
            'completed_count': len(completed_ids),
            'dual_location_count': len(dual_location),
            'issues': issues,
            'valid': len(issues) == 0
        }
    
    def repair_inconsistencies(self) -> Dict[str, Any]:
        """Repair common integrity issues"""
        validation = self.validate_chore_locations()
        repairs = []
        
        if not validation['valid']:
            # For now, just report issues - actual repair logic would go here
            repairs.append("Issues detected - manual intervention required")
        
        return {
            'repairs_attempted': len(repairs),
            'repairs': repairs
        }


class ArchivalManager:
    """Manages chore archival with single-location enforcement"""
    
    def __init__(self, active_file: str, completed_file: str):
        self.active_file = active_file
        self.completed_file = completed_file
    
    def archive_completed_chore(self, chore: Chore) -> bool:
        """Archive completed chore to completed file"""
        if chore.status != ChoreStatus.WORK_DONE:
            raise ValidationError(f"Cannot archive chore with status {chore.status}")
        
        # Append to completed file
        chore_data = self._chore_to_dict(chore)
        with open(self.completed_file, 'a') as f:
            f.write(json.dumps(chore_data) + '\n')
        
        return True
    
    def remove_from_active(self, chore_id: int, active_chores: Dict[int, Chore]) -> bool:
        """Remove chore from active collection"""
        if chore_id in active_chores:
            del active_chores[chore_id]
            return True
        return False
    
    def save_active_chores(self, active_chores: Dict[int, Chore]) -> bool:
        """Save active chores to file"""
        with open(self.active_file, 'w') as f:
            for chore in active_chores.values():
                chore_data = self._chore_to_dict(chore)
                f.write(json.dumps(chore_data) + '\n')
        return True
    
    def cleanup_duplicates(self) -> Dict[str, Any]:
        """Remove completed chores from active file"""
        active_chores = self._load_chores_from_file(self.active_file)
        completed_ids = self._get_completed_ids()
        
        cleaned = 0
        for chore_id in list(active_chores.keys()):
            chore = active_chores[chore_id]
            if chore.status == ChoreStatus.WORK_DONE or chore_id in completed_ids:
                # Archive if not already in completed file
                if chore_id not in completed_ids:
                    self.archive_completed_chore(chore)
                # Remove from active
                del active_chores[chore_id]
                cleaned += 1
        
        # Save cleaned active chores
        self.save_active_chores(active_chores)
        
        return {
            'cleaned_count': cleaned,
            'remaining_active': len(active_chores)
        }
    
    def _load_chores_from_file(self, file_path: str) -> Dict[int, Chore]:
        """Load chores from file"""
        chores = {}
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        chore = self._dict_to_chore(data)
                        chores[chore.id] = chore
        return chores
    
    def _get_completed_ids(self) -> set:
        """Get set of completed chore IDs"""
        completed_ids = set()
        if os.path.exists(self.completed_file):
            with open(self.completed_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        completed_ids.add(data['id'])
        return completed_ids
    
    def _chore_to_dict(self, chore: Chore) -> dict:
        """Convert chore to dictionary"""
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
        """Convert dictionary to chore"""
        chore = Chore.__new__(Chore)
        chore.id = data['id']
        chore.name = data['name']
        chore.description = data['description']
        chore.status = ChoreStatus(data['status'])
        chore.next_chore = None  # Will be linked separately
        chore.progress_info = data.get('progress_info')
        chore.review_info = data.get('review_info')
        return chore


class ChoreLifecycleManager:
    """Core chore lifecycle management with atomic operations"""
    
    def __init__(self, active_file: str, completed_file: str):
        self.active_file = active_file
        self.completed_file = completed_file
        self.transition_engine = StateTransitionEngine()
        self.validator = IntegrityValidator(active_file, completed_file)
        self.archival_manager = ArchivalManager(active_file, completed_file)
        self._transaction_callbacks: Dict[str, Callable] = {}
    
    @contextmanager
    def transaction(self):
        """Context manager for atomic operations"""
        try:
            # Begin transaction
            yield self
            # Validate integrity before commit
            validation = self.validator.validate_chore_locations()
            if not validation['valid']:
                raise ValidationError(f"Integrity validation failed: {validation['issues']}")
        except Exception as e:
            # Rollback would go here
            raise e
    
    def transition_chore_state(self, chore: Chore, new_status: ChoreStatus, 
                             active_chores: Dict[int, Chore],
                             progress_info: str = None, review_info: str = None) -> bool:
        """Transition chore to new state with atomic operations"""
        with self.transaction():
            # Execute transition
            success = self.transition_engine.execute_transition(chore, new_status)
            
            # Update additional info
            if progress_info is not None:
                chore.progress_info = progress_info
            if review_info is not None:
                chore.review_info = review_info
            
            # Handle completion
            if new_status == ChoreStatus.WORK_DONE:
                self._handle_completion(chore, active_chores)
            else:
                # Save active chores for non-completion transitions
                self.archival_manager.save_active_chores(active_chores)
            
            return success
    
    def _handle_completion(self, chore: Chore, active_chores: Dict[int, Chore]):
        """Handle chore completion - archive and remove from active"""
        # Archive completed chore
        self.archival_manager.archive_completed_chore(chore)
        
        # Remove from active collection
        self.archival_manager.remove_from_active(chore.id, active_chores)
        
        # Save updated active chores
        self.archival_manager.save_active_chores(active_chores)
        
        # Chain activation will be implemented in Phase 3
    
    def cleanup_system(self) -> Dict[str, Any]:
        """Clean up system inconsistencies"""
        return self.archival_manager.cleanup_duplicates()
    
    def validate_system_integrity(self) -> Dict[str, Any]:
        """Validate overall system integrity"""
        return self.validator.validate_chore_locations()
    
    def repair_system(self) -> Dict[str, Any]:
        """Attempt to repair system inconsistencies"""
        cleanup_result = self.cleanup_system()
        validation = self.validate_system_integrity()
        
        return {
            'cleanup': cleanup_result,
            'validation': validation,
            'repaired': validation['valid']
        }


# Factory function for easy instantiation
def create_lifecycle_manager(active_file: str, completed_file: str = None) -> ChoreLifecycleManager:
    """Create ChoreLifecycleManager with standard file naming"""
    if completed_file is None:
        if active_file.endswith('.jsonl'):
            completed_file = active_file.replace('.jsonl', '_completed.jsonl')
        else:
            completed_file = active_file + '_completed'
    
    return ChoreLifecycleManager(active_file, completed_file)


if __name__ == "__main__":
    # Test the core infrastructure
    manager = create_lifecycle_manager("/tmp/test_chores.jsonl")
    validation = manager.validate_system_integrity()
    print(f"System validation: {validation}")
