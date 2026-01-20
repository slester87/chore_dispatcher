#!/usr/bin/env python3
"""
ChoreDecomposer - Breaks down complex chores into manageable sub-chores.
"""

from typing import List, Dict, Any, Optional
from chore import Chore
from chore_repository import ChoreRepository
from chore_prompts import build_chore_planner_prompt


class ChoreDecomposer:
    """Decomposes complex chores into sub-chores with quality validation."""
    
    def __init__(self, repository: ChoreRepository):
        self.repository = repository
    
    def decompose_chore(self, parent_chore: Chore) -> List[Chore]:
        """Decompose a chore into sub-chores."""
        # Analyze codebase context
        context = self._analyze_codebase_context(parent_chore)
        
        # Generate sub-chore plan
        sub_chore_plan = self._generate_sub_chore_plan(parent_chore, context)
        
        # Validate quality criteria
        if not self._validate_quality_criteria(sub_chore_plan):
            raise ValueError("Sub-chore plan does not meet quality criteria")
        
        # Create and link sub-chores
        return self._create_sub_chores(parent_chore, sub_chore_plan)
    
    def _analyze_codebase_context(self, chore: Chore) -> Dict[str, Any]:
        """Analyze codebase context for the chore."""
        # This would integrate with code analysis tools
        # For now, return basic context
        return {
            'chore_id': chore.id,
            'chore_name': chore.name,
            'description': chore.description,
            'working_directory': '/Users/skippo/Development/KIRO'
        }
    
    def _generate_sub_chore_plan(self, chore: Chore, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate sub-chore plan using planner prompts."""
        # This would use the planner prompt to generate decomposition
        # For now, return a basic plan structure
        return [
            {
                'title': f"Sub-chore 1 for {chore.name}",
                'description': f"First part of {chore.description}",
                'scope_boundaries': "Handles initial setup",
                'broader_context': f"Part of parent chore {chore.id}",
                'success_criteria': "Implementation compiles and tests pass",
                'dependencies': []
            }
        ]
    
    def _validate_quality_criteria(self, sub_chore_plan: List[Dict[str, Any]]) -> bool:
        """Validate that sub-chores meet quality criteria."""
        for sub_chore in sub_chore_plan:
            if not self._check_specificity(sub_chore):
                return False
            if not self._check_context_constraint(sub_chore):
                return False
            if not self._check_containment(sub_chore):
                return False
            if not self._check_stability(sub_chore):
                return False
        return True
    
    def _check_specificity(self, sub_chore: Dict[str, Any]) -> bool:
        """Check if sub-chore has clear, unambiguous instructions."""
        return (
            'title' in sub_chore and 
            'description' in sub_chore and 
            len(sub_chore['description']) > 10
        )
    
    def _check_context_constraint(self, sub_chore: Dict[str, Any]) -> bool:
        """Check if sub-chore fits in reasonable context size."""
        # Simple heuristic: description length should be reasonable
        return len(sub_chore.get('description', '')) < 2000
    
    def _check_containment(self, sub_chore: Dict[str, Any]) -> bool:
        """Check if sub-chore is self-contained with clear boundaries."""
        return (
            'scope_boundaries' in sub_chore and 
            'broader_context' in sub_chore
        )
    
    def _check_stability(self, sub_chore: Dict[str, Any]) -> bool:
        """Check if sub-chore maintains production readiness."""
        return 'success_criteria' in sub_chore
    
    def _create_sub_chores(self, parent_chore: Chore, plan: List[Dict[str, Any]]) -> List[Chore]:
        """Create and link sub-chores based on the plan."""
        sub_chores = []
        
        for sub_chore_data in plan:
            sub_chore = self.repository.create_sub_chore(
                parent_id=parent_chore.id,
                name=sub_chore_data['title'],
                description=sub_chore_data['description']
            )
            if sub_chore:
                sub_chores.append(sub_chore)
        
        return sub_chores
