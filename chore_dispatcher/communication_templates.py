"""
Structured communication templates for Worker/Reviewer interaction.
Provides standardized formats for progress_info and review_info fields.
"""

from typing import Dict, List, Optional
from enum import Enum


class CommunicationType(Enum):
    PROGRESS_INFO = "progress_info"
    REVIEW_INFO = "review_info"


class ProgressTemplate:
    """Templates for Worker → Reviewer communication (progress_info)."""
    
    @staticmethod
    def design_progress(approach: str, patterns: List[str], rationale: str) -> str:
        """Template for design phase progress."""
        return f"""DESIGN PROGRESS:
• Approach: {approach}
• Patterns: {', '.join(patterns)}
• Rationale: {rationale}
• Status: Ready for design review"""
    
    @staticmethod
    def plan_progress(steps: List[str], dependencies: List[str], timeline: str, risks: List[str]) -> str:
        """Template for plan phase progress."""
        steps_text = '\n'.join([f"  {i+1}. {step}" for i, step in enumerate(steps)])
        deps_text = ', '.join(dependencies) if dependencies else 'None'
        risks_text = '\n'.join([f"  • {risk}" for risk in risks]) if risks else '  • None identified'
        
        return f"""PLAN PROGRESS:
• Implementation Steps:
{steps_text}
• Dependencies: {deps_text}
• Timeline: {timeline}
• Risks:
{risks_text}
• Status: Ready for plan review"""
    
    @staticmethod
    def work_progress(changes: List[str], testing: str, validation: str, concerns: Optional[str] = None) -> str:
        """Template for work phase progress."""
        changes_text = '\n'.join([f"  • {change}" for change in changes])
        concerns_text = f"\n• Concerns: {concerns}" if concerns else ""
        
        return f"""WORK PROGRESS:
• Code Changes:
{changes_text}
• Testing: {testing}
• Validation: {validation}{concerns_text}
• Status: Ready for work review"""


class ReviewTemplate:
    """Templates for Reviewer → Worker communication (review_info)."""
    
    @staticmethod
    def approve(phase: str, summary: str, next_guidance: Optional[str] = None) -> str:
        """Template for approval decision."""
        guidance_text = f"\n• Next Phase Guidance: {next_guidance}" if next_guidance else ""
        
        return f"""REVIEW DECISION: APPROVED
• Phase: {phase}
• Summary: {summary}{guidance_text}
• Status: Advancing to next phase"""
    
    @staticmethod
    def reject(phase: str, issues: List[str], requirements: List[str]) -> str:
        """Template for rejection with feedback."""
        issues_text = '\n'.join([f"  • {issue}" for issue in issues])
        reqs_text = '\n'.join([f"  • {req}" for req in requirements])
        
        return f"""REVIEW DECISION: NEEDS REWORK
• Phase: {phase}
• Issues Identified:
{issues_text}
• Required Changes:
{reqs_text}
• Status: Returned for revision"""
    
    @staticmethod
    def conditional(phase: str, approval: str, conditions: List[str]) -> str:
        """Template for conditional approval."""
        conds_text = '\n'.join([f"  • {cond}" for cond in conditions])
        
        return f"""REVIEW DECISION: CONDITIONAL APPROVAL
• Phase: {phase}
• Approval: {approval}
• Conditions for Next Phase:
{conds_text}
• Status: Approved with requirements"""


class CommunicationHelper:
    """Helper functions for structured communication."""
    
    @staticmethod
    def format_progress_info(template_func, **kwargs) -> str:
        """Format progress_info using template function."""
        try:
            return template_func(**kwargs)
        except Exception as e:
            return f"Progress update error: {str(e)}"
    
    @staticmethod
    def format_review_info(template_func, **kwargs) -> str:
        """Format review_info using template function."""
        try:
            return template_func(**kwargs)
        except Exception as e:
            return f"Review feedback error: {str(e)}"
    
    @staticmethod
    def parse_progress_info(progress_text: str) -> Dict[str, str]:
        """Parse structured progress_info into components."""
        if not progress_text:
            return {}
        
        components = {}
        current_key = None
        current_value = []
        
        for line in progress_text.split('\n'):
            if line.startswith('• ') and ':' in line:
                if current_key:
                    components[current_key] = '\n'.join(current_value).strip()
                current_key = line[2:].split(':')[0].strip()
                current_value = [line[2:].split(':', 1)[1].strip()]
            elif current_key and line.strip():
                current_value.append(line)
        
        if current_key:
            components[current_key] = '\n'.join(current_value).strip()
        
        return components
    
    @staticmethod
    def parse_review_info(review_text: str) -> Dict[str, str]:
        """Parse structured review_info into components."""
        if not review_text:
            return {}
        
        components = {}
        lines = review_text.split('\n')
        
        if lines and 'REVIEW DECISION:' in lines[0]:
            components['decision'] = lines[0].split(':', 1)[1].strip()
        
        current_key = None
        current_value = []
        
        for line in lines[1:]:
            if line.startswith('• ') and ':' in line:
                if current_key:
                    components[current_key] = '\n'.join(current_value).strip()
                current_key = line[2:].split(':')[0].strip()
                current_value = [line[2:].split(':', 1)[1].strip()]
            elif current_key and line.strip():
                current_value.append(line)
        
        if current_key:
            components[current_key] = '\n'.join(current_value).strip()
        
        return components


# Example usage functions
def example_design_progress():
    """Example of design phase progress reporting."""
    return ProgressTemplate.design_progress(
        approach="Component-based architecture with dependency injection",
        patterns=["Factory Pattern", "Observer Pattern", "Strategy Pattern"],
        rationale="Ensures loose coupling and high testability"
    )

def example_work_review_approval():
    """Example of work review approval."""
    return ReviewTemplate.approve(
        phase="work",
        summary="Implementation meets all quality standards with comprehensive testing",
        next_guidance="Ready for production deployment"
    )

def example_plan_review_rejection():
    """Example of plan review rejection."""
    return ReviewTemplate.reject(
        phase="plan",
        issues=["Missing error handling strategy", "No performance considerations", "Incomplete testing plan"],
        requirements=["Add comprehensive error handling", "Include performance benchmarks", "Define test coverage targets"]
    )
