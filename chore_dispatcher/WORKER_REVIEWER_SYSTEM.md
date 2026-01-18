# Worker/Reviewer Agent System

## Overview

The chore system now enforces role-based separation between Worker and Reviewer agents:

- **Worker Agent**: Handles `design`, `plan`, and `work` states
- **Reviewer Agent**: Handles `design_review`, `plan_review`, and `work_review` states

## Communication

Agents communicate through dedicated fields in the Chore object:

- **ProgressInfo**: Worker → Reviewer communication
- **ReviewerInfo**: Reviewer → Worker communication

## MCP Tools

### Worker Agent Tools

- `worker_update_progress(chore_id, progress_info)`: Update progress during work phases
- `worker_advance_to_review(chore_id, progress_info)`: Complete work and advance to review
- `get_worker_chores()`: Get all chores in worker states

### Reviewer Agent Tools

- `reviewer_update_feedback(chore_id, review_info)`: Provide feedback during review phases
- `reviewer_approve_or_reject(chore_id, approved, review_info)`: Approve or reject work
- `get_reviewer_chores()`: Get all chores in reviewer states

## Workflow

1. **Worker** creates/works on chore in `design` state
2. **Worker** updates progress via `worker_update_progress()`
3. **Worker** completes work and advances to `design_review` via `worker_advance_to_review()`
4. **Reviewer** reviews work and provides feedback via `reviewer_update_feedback()`
5. **Reviewer** approves (→ `design_ready`) or rejects (→ `design`) via `reviewer_approve_or_reject()`
6. Process repeats for `plan` → `plan_review` → `plan_ready`
7. Process repeats for `work` → `work_review` → `work_done`

## State Transitions

```
design → design_review → design_ready → plan → plan_review → plan_ready → work → work_review → work_done
  ↑         ↓                            ↑         ↓                        ↑         ↓
Worker    Reviewer                     Worker    Reviewer                Worker    Reviewer
```

## Example Usage

```python
# Worker starts design
worker_update_progress(chore_id, "Initial design concepts drafted")

# Worker completes design
worker_advance_to_review(chore_id, "Design complete, ready for review")

# Reviewer provides feedback
reviewer_update_feedback(chore_id, "Design looks good, minor adjustments needed")

# Reviewer approves
reviewer_approve_or_reject(chore_id, True, "Approved - proceed to planning")
```
