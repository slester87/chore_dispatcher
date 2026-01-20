#!/usr/bin/env python3
"""
Dispatcher Hooks for Chore Lifecycle Integration

Connects chore state transitions to TMUX dispatcher actions.
"""

import logging
from typing import Optional
from chore_dispatcher import ChoreDispatcher
from chore import Chore, ChoreStatus

logger = logging.getLogger(__name__)

class DispatcherHooks:
    """Hooks chore lifecycle events to dispatcher actions."""
    
    def __init__(self, dispatcher: Optional[ChoreDispatcher] = None):
        self.dispatcher = dispatcher or ChoreDispatcher()
        
    def on_chore_state_change(self, chore: Chore, old_status: ChoreStatus, new_status: ChoreStatus) -> None:
        """Handle chore state transitions."""
        try:
            # Create worker window for design and work phases
            if new_status in [ChoreStatus.DESIGN, ChoreStatus.WORK]:
                if old_status not in [ChoreStatus.DESIGN, ChoreStatus.PLAN, ChoreStatus.WORK]:
                    logger.info(f"Creating worker window for chore {chore.id} ({new_status.value})")
                    self.dispatcher.create_worker_window(chore)
                    
            # Create planner pane for plan phase
            elif new_status == ChoreStatus.PLAN:
                logger.info(f"Creating planner pane for chore {chore.id} ({new_status.value})")
                self.dispatcher.create_planner_pane(chore)
                    
            # Create reviewer pane for review phases
            elif new_status in [ChoreStatus.DESIGN_REVIEW, ChoreStatus.PLAN_REVIEW, ChoreStatus.WORK_REVIEW]:
                logger.info(f"Creating reviewer pane for chore {chore.id} ({new_status.value})")
                self.dispatcher.create_reviewer_pane(chore)
                    
            # Cleanup window when work is done
            elif new_status == ChoreStatus.WORK_DONE:
                logger.info(f"Cleaning up worker window for completed chore {chore.id}")
                self.dispatcher.cleanup_worker_window(chore.id)
                
            # Cleanup planner pane when transitioning out of plan phase
            if old_status == ChoreStatus.PLAN and new_status != ChoreStatus.PLAN:
                logger.info(f"Cleaning up planner pane for chore {chore.id}")
                self.dispatcher.cleanup_planner_pane(chore)
                
            # Cleanup reviewer pane when transitioning out of review phases
            if old_status in [ChoreStatus.DESIGN_REVIEW, ChoreStatus.PLAN_REVIEW, ChoreStatus.WORK_REVIEW]:
                if new_status not in [ChoreStatus.DESIGN_REVIEW, ChoreStatus.PLAN_REVIEW, ChoreStatus.WORK_REVIEW]:
                    logger.info(f"Cleaning up reviewer pane for chore {chore.id}")
                    self.dispatcher.cleanup_reviewer_pane(chore)
                
            # Update context when status changes
            if old_status != new_status:
                self.dispatcher.update_chore_context(chore)
                # Rename window to reflect new status
                self.dispatcher.rename_chore_window(chore)
                
        except Exception as e:
            logger.error(f"Dispatcher hook failed for chore {chore.id}: {e}")
            
    def on_chore_created(self, chore: Chore) -> None:
        """Handle new chore creation."""
        # Chores start in DESIGN, so create window immediately
        if chore.status == ChoreStatus.DESIGN:
            logger.info(f"Creating worker window for new chore {chore.id}")
            self.dispatcher.create_worker_window(chore)
            
    def on_chore_deleted(self, chore_id: int) -> None:
        """Handle chore deletion."""
        logger.info(f"Cleaning up worker window for deleted chore {chore_id}")
        self.dispatcher.cleanup_worker_window(chore_id)

# Global dispatcher hooks instance
_dispatcher_hooks: Optional[DispatcherHooks] = None

def get_dispatcher_hooks() -> DispatcherHooks:
    """Get global dispatcher hooks instance."""
    global _dispatcher_hooks
    if _dispatcher_hooks is None:
        _dispatcher_hooks = DispatcherHooks()
    return _dispatcher_hooks

def initialize_dispatcher_hooks(dispatcher: Optional[ChoreDispatcher] = None) -> DispatcherHooks:
    """Initialize global dispatcher hooks."""
    global _dispatcher_hooks
    _dispatcher_hooks = DispatcherHooks(dispatcher)
    return _dispatcher_hooks
