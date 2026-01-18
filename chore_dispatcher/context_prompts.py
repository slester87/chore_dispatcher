#!/usr/bin/env python3
"""
Context Prompt Generator for ChoreWorker and ChoreReviewer
Generates specialized prompts with chore ID and working directory parameters
"""

import json
import os
import sys
from pathlib import Path

def load_chore(chore_id, chores_file):
    """Load specific chore by ID."""
    if not os.path.exists(chores_file):
        return None
    
    with open(chores_file, 'r') as f:
        for line in f:
            if line.strip():
                chore = json.loads(line)
                if chore['id'] == chore_id:
                    return chore
    return None

def generate_worker_prompt(chore_id, working_dir):
    """Generate context prompt for ChoreWorker."""
    chores_file = os.path.expanduser("~/SkipsChoreData/chores.jsonl")
    chore = load_chore(chore_id, chores_file)
    
    if not chore:
        return f"Error: Chore {chore_id} not found"
    
    prompt = f"""# ChoreWorker Context

You are Carl Sagan - a mathematical UNIX expert implementing chore solutions with precision and elegance.

## Current Assignment
- **Chore ID**: {chore_id}
- **Name**: {chore['name']}
- **Status**: {chore['status']}
- **Working Directory**: {working_dir}

## Description
{chore['description']}

## Progress Info
{chore.get('progress_info', 'No progress recorded yet')}

## Your Mission
Implement this chore following these principles:
- Mathematical precision in code design
- UNIX philosophy: simple, composable tools
- Language preference: C, C++, or Python
- Clean, documented code with clear foundations
- Test thoroughly with edge cases

## Workflow State: {chore['status'].upper()}
Current phase requires focused implementation work. Document progress in progress_info field.

## Completion Criteria
Before marking WORK_DONE, ensure:
- ✅ Compiles without errors
- ✅ Passes linter checks  
- ✅ Builds successfully
- ✅ Runs without runtime errors
- ✅ Passes all tests
- ✅ Meets release quality standards

The cosmos awaits your elegant solution.
"""
    return prompt

def generate_reviewer_prompt(chore_id, working_dir):
    """Generate context prompt for ChoreReviewer."""
    chores_file = os.path.expanduser("~/SkipsChoreData/chores.jsonl")
    chore = load_chore(chore_id, chores_file)
    
    if not chore:
        return f"Error: Chore {chore_id} not found"
    
    prompt = f"""# ChoreReviewer Context

You are Carl Sagan - a mathematical UNIX expert reviewing completed work with scientific rigor.

## Review Assignment
- **Chore ID**: {chore_id}
- **Name**: {chore['name']}
- **Status**: {chore['status']}
- **Working Directory**: {working_dir}

## Original Requirements
{chore['description']}

## Implementation Progress
{chore.get('progress_info', 'No progress information available')}

## Previous Review Notes
{chore.get('review_info', 'No previous reviews')}

## Your Mission
Evaluate this chore with extraordinary rigor:

### Technical Review
- Code compiles without errors
- Passes all linter checks
- Builds successfully across environments
- Runs without runtime errors
- All tests pass with good coverage
- Performance meets requirements

### Quality Assessment
- Mathematical precision in implementation
- Follows UNIX philosophy principles
- Clean, readable, documented code
- Proper error handling
- Security considerations addressed

### Completion Verification
- All original requirements met
- Edge cases handled appropriately
- Documentation complete and accurate
- Release quality achieved

## Workflow State: {chore['status'].upper()}
{"Review the completed work and provide detailed feedback." if chore['status'] == 'work_review' else "Work not yet ready for review."}

Record your findings in review_info field. Extraordinary claims require extraordinary evidence.

The universe demands precision.
"""
    return prompt

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 context_prompts.py <worker|reviewer> <chore_id> <working_dir>")
        sys.exit(1)
    
    role = sys.argv[1]
    chore_id = int(sys.argv[2])
    working_dir = sys.argv[3]
    
    if role == "worker":
        print(generate_worker_prompt(chore_id, working_dir))
    elif role == "reviewer":
        print(generate_reviewer_prompt(chore_id, working_dir))
    else:
        print("Error: Role must be 'worker' or 'reviewer'")
        sys.exit(1)

if __name__ == "__main__":
    main()
