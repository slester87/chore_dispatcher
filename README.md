# Chore Dispatcher

A task management system that tracks work through a structured workflow with unique identifiers and chaining capabilities.

## Overview

The Chore Dispatcher manages tasks (chores) through a 9-stage workflow, from initial design to completion. Each chore gets a unique Snowflake ID and can be chained to trigger follow-up work.

## Chore Workflow

Chores progress through these states:

1. **DESIGN** - Define what needs to be done
2. **DESIGN_REVIEW** - Review the design
3. **DESIGN_READY** - Design approved, ready for planning
4. **PLAN** - Create implementation plan
5. **PLAN_REVIEW** - Review the plan
6. **PLAN_READY** - Plan approved, ready for work
7. **WORK** - Active development/implementation
8. **WORK_REVIEW** - Review completed work
9. **WORK_DONE** - Work complete and approved

## Completion Standards

Before marking a chore as **WORK_DONE**, it must:

- ✅ Compile without errors
- ✅ Pass linter checks
- ✅ Build successfully
- ✅ Run without runtime errors
- ✅ Pass all tests
- ✅ Meet release quality standards

## Core Components

### Chore Class
- Unique Snowflake ID generation
- Status progression through workflow
- Chaining to next chore when complete

### ChoreRepository
Full CRUD operations:
- `create(name, description)` - Create new chore
- `read(chore_id)` - Get chore by ID
- `update(chore_id, ...)` - Update chore properties
- `delete(chore_id)` - Remove chore
- `list_all()` - Get all chores
- `find_by_status(status)` - Filter by status

## Usage Example

```python
from chore import Chore, ChoreStatus
from chore_repository import ChoreRepository

# Create repository
repo = ChoreRepository()

# Create a chore
chore = repo.create("Implement user login", "Add authentication system")

# Progress through workflow
chore.advance_status()  # DESIGN -> DESIGN_REVIEW
chore.advance_status()  # DESIGN_REVIEW -> DESIGN_READY

# Chain chores
next_chore = repo.create("Add user dashboard", "Create user interface")
chore.set_next_chore(next_chore)

# Check completion
if chore.is_complete():
    next_task = chore.get_next_chore()
```

## Testing

Run tests before pushing:
```bash
python3 chore_dispatcher/test_chore.py
```

Tests are automatically run via git pre-push hook to ensure code quality.

## Files

- `chore.py` - Core Chore class and status enum
- `chore_repository.py` - CRUD operations
- `chore_src/snowflake.py` - Unique ID generator
- `test_chore.py` - Comprehensive test suite
- `agents.md` - Quality standards and guidelines
