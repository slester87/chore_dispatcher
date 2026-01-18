# Chore Lifecycle Management System Design

## Current System Analysis

### Architecture Components
- **chore.py**: Core Chore class with 9-state workflow
- **chore_repository.py**: CRUD operations with archival logic
- **chore_mcp_server.py**: API layer for external access
- **tmux_chore_status.py**: Real-time status display
- **context_prompts.py**: Agent context generation
- **test_chore.py**: Validation suite

### Identified Issues
1. **Dual-location existence**: Completed chores remain in active file
2. **Broken chaining**: next_chore not activated on completion
3. **Inconsistent archival**: Manual cleanup required
4. **State transition gaps**: Missing atomic operations

## Proposed Solution: ChoreLifecycleManager

### Core Principles
1. **Single Source of Truth**: Chore exists in exactly one location
2. **Atomic Operations**: State changes are all-or-nothing
3. **Automatic Transitions**: System handles lifecycle without manual intervention
4. **Chain Activation**: Completed chores trigger next chore automatically
5. **Validation**: Continuous integrity checking

### System Architecture

```
ChoreLifecycleManager
├── StateTransitionEngine
│   ├── validate_transition()
│   ├── execute_transition()
│   └── rollback_on_failure()
├── ArchivalManager
│   ├── archive_completed_chore()
│   ├── validate_single_location()
│   └── cleanup_duplicates()
├── ChainActivationEngine
│   ├── activate_next_chore()
│   ├── validate_chain_integrity()
│   └── handle_chain_completion()
└── IntegrityValidator
    ├── validate_chore_locations()
    ├── detect_orphaned_chores()
    └── repair_inconsistencies()
```

### State Transition Rules

#### Valid Transitions
```
DESIGN → DESIGN_REVIEW → DESIGN_READY → PLAN → PLAN_REVIEW → PLAN_READY → WORK → WORK_REVIEW → WORK_DONE
```

#### Transition Actions
- **To WORK_DONE**: Archive chore + Activate next chore + Remove from active
- **All others**: Update status + Save to active file

### File Management Strategy

#### Active Chores (chores.jsonl)
- Contains chores in states: DESIGN through WORK_REVIEW
- Updated atomically on state changes
- Validated for completeness on each operation

#### Completed Chores (chores_completed.jsonl)
- Contains chores in WORK_DONE state only
- Append-only operations for performance
- Immutable once archived

### Atomic Operation Protocol

```python
def transition_chore_state(chore_id, new_status):
    with transaction():
        # 1. Validate transition
        if not validate_transition(chore_id, new_status):
            raise InvalidTransition()
        
        # 2. Execute state change
        chore = update_chore_status(chore_id, new_status)
        
        # 3. Handle completion
        if new_status == WORK_DONE:
            archive_chore(chore)
            activate_next_chore(chore.next_chore_id)
            remove_from_active(chore_id)
        
        # 4. Validate integrity
        validate_system_integrity()
        
        # 5. Commit changes
        commit_transaction()
```

### Chain Activation Logic

```python
def activate_next_chore(next_chore_id):
    if next_chore_id:
        next_chore = load_chore(next_chore_id)
        if next_chore and next_chore.status == DESIGN:
            # Next chore becomes available for work
            log_chain_activation(next_chore_id)
```

### Validation Rules

#### Location Validation
- Chore exists in exactly one file (active OR completed)
- No chore exists in both files simultaneously
- All active chores have valid status (not WORK_DONE)
- All completed chores have WORK_DONE status

#### Chain Validation
- next_chore_id references exist or are null
- No circular chains
- Chain integrity maintained across transitions

### Implementation Plan

#### Phase 1: Core Infrastructure
1. Create ChoreLifecycleManager class
2. Implement StateTransitionEngine
3. Add atomic transaction support
4. Create validation framework

#### Phase 2: Archival System
1. Implement ArchivalManager
2. Add location validation
3. Create cleanup utilities
4. Ensure single-location existence

#### Phase 3: Chain Management
1. Implement ChainActivationEngine
2. Add chain validation
3. Handle chain completion events
4. Test complex chain scenarios

#### Phase 4: Integration
1. Update ChoreRepository to use lifecycle manager
2. Modify MCP server for new operations
3. Update tests for new behavior
4. Add monitoring and diagnostics

### Error Handling

#### Recovery Strategies
- **Dual-location**: Remove from active, keep in completed
- **Missing chore**: Restore from backup or recreate
- **Invalid state**: Reset to last valid state
- **Broken chain**: Log error, continue without chain

#### Monitoring
- Daily integrity checks
- Automatic repair of common issues
- Alerting for critical failures
- Performance metrics tracking

### Performance Considerations

#### Optimization Strategies
- Lazy loading of chore data
- Batch operations for multiple transitions
- Caching of frequently accessed chores
- Asynchronous archival operations

#### Scalability
- Support for thousands of chores
- Efficient file I/O operations
- Memory-conscious data structures
- Parallel processing where safe

### Testing Strategy

#### Unit Tests
- State transition validation
- Archival operations
- Chain activation logic
- Error handling scenarios

#### Integration Tests
- End-to-end workflow testing
- File system integrity
- Concurrent operation safety
- Performance benchmarks

### Migration Plan

#### Existing Data
1. Validate current chore locations
2. Clean up dual-location chores
3. Repair broken chains
4. Migrate to new system gradually

#### Backward Compatibility
- Maintain existing API contracts
- Support legacy file formats during transition
- Provide migration utilities
- Document breaking changes

This design ensures robust, reliable chore lifecycle management with atomic operations, automatic archival, and chain activation while maintaining system integrity.
