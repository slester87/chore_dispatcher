#!/usr/bin/env python3
"""
ChoreReviewer - Reviews chore decomposition plans for quality compliance.
"""

from typing import List, Dict, Any, Optional
from chore import Chore
from chore_repository import ChoreRepository


class ChoreReviewer:
    """Reviews chore decomposition plans with comprehensive quality assessment."""
    
    def __init__(self, repository: ChoreRepository):
        self.repository = repository
    
    def review_decomposition(self, parent_chore: Chore, sub_chore_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Review a decomposition plan and provide assessment."""
        evaluation_results = {
            'overall_assessment': 'NEEDS_REVISION',
            'specific_issues': [],
            'boundary_problems': [],
            'context_issues': [],
            'quality_concerns': [],
            'recommendations': []
        }
        
        # Evaluate each sub-chore
        for i, sub_chore in enumerate(sub_chore_plan):
            sub_chore_id = f"sub-chore-{i+1}"
            
            if not self._evaluate_specificity(sub_chore):
                evaluation_results['specific_issues'].append(f"{sub_chore_id}: Lacks clear, specific instructions")
            
            if not self._evaluate_context_constraint(sub_chore):
                evaluation_results['context_issues'].append(f"{sub_chore_id}: May exceed context constraints")
            
            if not self._evaluate_containment(sub_chore):
                evaluation_results['boundary_problems'].append(f"{sub_chore_id}: Unclear scope boundaries")
            
            if not self._evaluate_stability(sub_chore):
                evaluation_results['quality_concerns'].append(f"{sub_chore_id}: Stability requirements not met")
            
            if not self._check_algorithm_validation(sub_chore):
                evaluation_results['quality_concerns'].append(f"{sub_chore_id}: Algorithm validation missing")
        
        # Generate overall assessment
        if not any([
            evaluation_results['specific_issues'],
            evaluation_results['boundary_problems'], 
            evaluation_results['context_issues'],
            evaluation_results['quality_concerns']
        ]):
            evaluation_results['overall_assessment'] = 'APPROVED'
        
        # Generate feedback
        evaluation_results['feedback'] = self._generate_feedback(evaluation_results)
        
        return evaluation_results
    
    def _evaluate_specificity(self, sub_chore: Dict[str, Any]) -> bool:
        """Evaluate if sub-chore has clear, specific instructions."""
        if not sub_chore.get('description'):
            return False
        
        description = sub_chore['description']
        
        # Check for semantic code locations (not line numbers)
        has_semantic_locations = any(phrase in description.lower() for phrase in [
            'in the', 'where', 'handler', 'method', 'class', 'function', 'module'
        ])
        
        # Check against line number references
        has_line_numbers = any(phrase in description.lower() for phrase in [
            'line', 'lines', 'first', 'next', 'count'
        ])
        
        return has_semantic_locations and not has_line_numbers and len(description) > 50
    
    def _evaluate_context_constraint(self, sub_chore: Dict[str, Any]) -> bool:
        """Evaluate if sub-chore fits in reasonable context size."""
        description = sub_chore.get('description', '')
        
        # Simple heuristic: reasonable description length
        if len(description) > 1500:
            return False
        
        # Check for scope indicators
        scope_indicators = ['one file', 'few files', 'single', 'specific']
        has_scope_control = any(indicator in description.lower() for indicator in scope_indicators)
        
        return has_scope_control
    
    def _evaluate_containment(self, sub_chore: Dict[str, Any]) -> bool:
        """Evaluate if sub-chore is self-contained with clear boundaries."""
        required_fields = ['scope_boundaries', 'broader_context']
        
        for field in required_fields:
            if not sub_chore.get(field):
                return False
        
        # Check for boundary clarity
        boundaries = sub_chore.get('scope_boundaries', '')
        has_includes = 'includes' in boundaries.lower() or 'handles' in boundaries.lower()
        has_excludes = 'excludes' in boundaries.lower() or 'not' in boundaries.lower()
        
        return has_includes and len(boundaries) > 20
    
    def _evaluate_stability(self, sub_chore: Dict[str, Any]) -> bool:
        """Evaluate if sub-chore maintains production readiness."""
        success_criteria = sub_chore.get('success_criteria', '')
        
        if not success_criteria:
            return False
        
        # Check for quality indicators
        quality_indicators = ['compiles', 'tests', 'builds', 'lints', 'passes']
        has_quality_checks = any(indicator in success_criteria.lower() for indicator in quality_indicators)
        
        return has_quality_checks and len(success_criteria) > 30
    
    def _check_algorithm_validation(self, sub_chore: Dict[str, Any]) -> bool:
        """Check if algorithm validation is present for complex sub-chores."""
        description = sub_chore.get('description', '')
        
        # Check if this involves algorithms
        algorithm_keywords = ['algorithm', 'complexity', 'performance', 'optimization', 'data structure']
        involves_algorithms = any(keyword in description.lower() for keyword in algorithm_keywords)
        
        if not involves_algorithms:
            return True  # No algorithm validation needed
        
        # Check for validation elements
        validation_keywords = ['correctness', 'complexity analysis', 'edge cases', 'invariants']
        has_validation = any(keyword in description.lower() for keyword in validation_keywords)
        
        return has_validation
    
    def _generate_feedback(self, evaluation_results: Dict[str, Any]) -> str:
        """Generate structured feedback based on evaluation results."""
        feedback_parts = []
        
        if evaluation_results['overall_assessment'] == 'APPROVED':
            feedback_parts.append("**APPROVED** - Decomposition plan meets all quality criteria.")
        else:
            feedback_parts.append("**NEEDS REVISION** - Issues identified that must be addressed:")
        
        if evaluation_results['specific_issues']:
            feedback_parts.append("\n**Specificity Issues:**")
            for issue in evaluation_results['specific_issues']:
                feedback_parts.append(f"- {issue}")
        
        if evaluation_results['boundary_problems']:
            feedback_parts.append("\n**Boundary Problems:**")
            for problem in evaluation_results['boundary_problems']:
                feedback_parts.append(f"- {problem}")
        
        if evaluation_results['context_issues']:
            feedback_parts.append("\n**Context Issues:**")
            for issue in evaluation_results['context_issues']:
                feedback_parts.append(f"- {issue}")
        
        if evaluation_results['quality_concerns']:
            feedback_parts.append("\n**Quality Concerns:**")
            for concern in evaluation_results['quality_concerns']:
                feedback_parts.append(f"- {concern}")
        
        return '\n'.join(feedback_parts)
    
    def approve(self, parent_chore: Chore, sub_chore_plan: List[Dict[str, Any]]) -> bool:
        """Approve a decomposition plan."""
        review_result = self.review_decomposition(parent_chore, sub_chore_plan)
        return review_result['overall_assessment'] == 'APPROVED'
    
    def reject(self, parent_chore: Chore, sub_chore_plan: List[Dict[str, Any]], feedback: str) -> Dict[str, Any]:
        """Reject a decomposition plan with feedback."""
        return {
            'status': 'REJECTED',
            'feedback': feedback,
            'parent_chore_id': parent_chore.id
        }
