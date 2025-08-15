# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains a comprehensive automated development workflow system for Claude Code CLI. It implements a Test-Driven Development (TDD) approach with multi-agent orchestration, enabling autonomous execution of complex development tasks through a resilient state machine architecture.

## High-Level Architecture

### Core Components

1. **Orchestrator Script (`automate_dev.py`)**: Python-based workflow controller that manages the entire TDD loop
2. **State Management (`Implementation_Plan.md`)**: Markdown-based task checklist serving as the single source of truth
3. **Custom Slash Commands (`.claude/commands/`)**: Encapsulated, repeatable agent actions
4. **Signal-Based Completion Detection**: Hook-driven signaling for reliable task completion
5. **MCP Server Integration**: Structured status reporting through tool calls

### Key Design Patterns

- **Transactional State Management**: Only `/update` command modifies state after successful validation
- **Circuit Breaker Pattern**: Per-task failure tracking with MAX_FIX_ATTEMPTS (default: 3)
- **Event-Driven Architecture**: Stop hook provides definitive completion signals
- **External State Machine**: Implementation_Plan.md provides durable, recoverable state

## Commands

### Development and Testing

```bash
# Install dependencies
pip install pytz pytest

# Run tests (when implemented)
pytest tests/

# Start automation orchestrator
python automate_dev.py
```

### Custom Slash Commands

- `/continue` - Implement next task from Implementation_Plan.md using TDD
- `/validate` - Run tests and quality checks, report status
- `/update` - Mark current task complete (only after validation)
- `/correct` - Fix validation failures based on error details
- `/checkin` - Comprehensive project review and requirements verification
- `/refactor` - Identify refactoring opportunities
- `/finalize` - Implement refactoring tasks

## TDD Workflow

### Red-Green-Refactor Cycle

1. **Red Phase**: Use `test-writer` agent to create failing test
2. **Green Phase**: Use `implementation-verifier` agent to write minimal passing code
3. **Refactor Phase**: Use `refactoring-specialist` agent to improve code quality

### Agent Orchestration

The system uses specialized agents for each phase:
- `test-writer`: Creates one failing test at a time following FIRST principles
- `implementation-verifier`: Implements minimal code to make tests pass
- `refactoring-specialist`: Improves code while maintaining green tests

## Critical Implementation Details

### File Naming Convention
- Always use `Implementation_Plan.md` (not `tasks.md`)
- Status files use timestamp pattern: `status_[timestamp].json`

### Required CLI Flags
```bash
claude -p "/command" --output-format json --dangerously-skip-permissions
```

### Hook Configuration
The Stop hook in `.claude/settings.local.json` creates signal files for completion detection:
```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "touch .claude/signal_task_complete"
      }]
    }]
  }
}
```

### Usage Limit Handling
The system automatically detects and recovers from Claude Max usage limits:
- Parses reset time from error messages
- Displays countdown timer
- Automatically resumes workflow after reset

## Development Standards

### Code Quality Requirements
- All tests must pass before marking tasks complete
- Linting and type checking must succeed
- Follow existing code conventions and patterns
- Never commit broken code

### State Management Rules
- Tasks marked with `[ ]` are incomplete
- Tasks marked with `[X]` are complete
- Only `/update` command can modify task state
- State changes only occur after successful validation

### Error Handling
- Maximum 3 fix attempts per task before manual intervention
- Comprehensive logging to `.claude/logs/`
- Graceful degradation on permanent failures

## Project-Specific Context

This project focuses on automating Claude Code CLI workflows through:
- Reliable session completion detection via Stop hooks
- Structured status reporting through MCP servers
- Resilient state management with Implementation_Plan.md
- Comprehensive error recovery including usage limit handling

The architecture prioritizes reliability over speed, using proven patterns from distributed systems to ensure predictable, recoverable automation.

## Development Status (Last Updated: 2025-08-15)

### PROJECT v1.3.2 - Comprehensive Type Hints Complete 🚀

Core functionality complete (Phases 0-10) with 100% test coverage.
Phase 11 (Code Quality Refactoring) - All 6 tasks complete.
Phase 12 (Architecture and Design) - Tasks 1-4 complete:
  - ✅ Task 12.1: Extract TaskTracker to separate module
  - ✅ Task 12.2: Create dedicated modules for specialized functionality
  - ✅ Task 12.3: Implement proper dependency injection
  - ✅ Task 12.4: Add comprehensive type hints with TypedDict
Remaining: Task 12.5 (logging architecture).
All tests passing with comprehensive type safety and enhanced IDE support.

### Completed Components
- ✅ Phase 0: Project Initialization and Prerequisite Setup
- ✅ Phase 1: Core orchestrator with prerequisite checks
- ✅ Phase 2: TaskTracker class with failure tracking
- ✅ Phase 3: Claude command execution with signal handling
- ✅ Phase 4: MCP Server for status reporting
- ✅ Phase 5: All custom slash commands implemented
- ✅ Phase 6: Hook configuration with Stop signal
- ✅ Phase 7: Main orchestration loop with correction path
- ✅ Phase 8: Refactoring and finalization loop
- ✅ Phase 9: Usage limit handling with automatic recovery
- ✅ Phase 10: Comprehensive logging and documentation

### Key Features
- Full TDD implementation with multi-agent orchestration
- Resilient state management with automatic failure recovery
- Comprehensive logging with 6 module-specific loggers
- Complete documentation (README.md, CHANGELOG.md)
- Production-ready with robust error handling
- Modular architecture with separated concerns:
  - `task_tracker.py` - Task state management
  - `usage_limit.py` - API limit handling
  - `signal_handler.py` - Signal file operations
  - `command_executor.py` - Command execution logic