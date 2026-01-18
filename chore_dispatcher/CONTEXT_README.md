# Context Prompts for ChoreWorker and ChoreReviewer

Parameterized context generation for specialized chore agents.

## Usage

```bash
# Generate worker context
python3 context_prompts.py worker <chore_id> <working_directory>

# Generate reviewer context  
python3 context_prompts.py reviewer <chore_id> <working_directory>
```

## Examples

```bash
# Worker prompt for chore 271055724300210176
python3 context_prompts.py worker 271055724300210176 /Users/skippo/Development/KIRO

# Reviewer prompt for same chore
python3 context_prompts.py reviewer 271055724300210176 /Users/skippo/Development/KIRO
```

## Features

- **Dynamic chore loading** from SkipsChoreData
- **Role-specific prompts** with appropriate focus
- **Carl Sagan persona** with mathematical precision
- **Progress tracking** via progress_info and review_info fields
- **Workflow state awareness** for contextual guidance
- **Completion criteria** embedded in prompts

## Prompt Structure

### ChoreWorker
- Current assignment details
- Implementation guidance
- Completion criteria checklist
- Progress documentation instructions

### ChoreReviewer  
- Review assignment details
- Technical review checklist
- Quality assessment criteria
- Previous review history
