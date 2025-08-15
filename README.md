# Claude Code Automated Development Workflow

A resilient, automated development loop system for Claude Code CLI that implements Test-Driven Development (TDD) with multi-agent orchestration.

## Overview

This project provides a comprehensive automation framework for Claude Code CLI, enabling autonomous execution of complex development tasks through a resilient state machine architecture. It follows strict TDD methodology with specialized agents for each phase of the development cycle.

## Features

- **Test-Driven Development (TDD)**: Strict Red-Green-Refactor cycle with multi-agent orchestration
- **Resilient State Management**: Markdown-based task tracking with automatic failure recovery
- **Signal-Based Completion Detection**: Hook-driven signaling for reliable task completion
- **Usage Limit Handling**: Automatic detection and recovery from Claude API usage limits
- **Comprehensive Logging**: Module-specific logging with timestamped log files
- **MCP Server Integration**: Structured status reporting through tool calls

## Architecture

### Core Components

1. **Orchestrator Script (`automate_dev.py`)**: Python-based workflow controller managing the entire TDD loop
2. **State Management (`Implementation_Plan.md`)**: Markdown-based task checklist serving as the single source of truth
3. **Custom Slash Commands (`.claude/commands/`)**: Encapsulated, repeatable agent actions
4. **MCP Server (`status_mcp_server.py`)**: Provides structured status reporting
5. **Test Suite (`tests/`)**: Comprehensive test coverage with 35+ tests

### Key Design Patterns

- **Transactional State Management**: Only `/update` command modifies state after successful validation
- **Circuit Breaker Pattern**: Per-task failure tracking with MAX_FIX_ATTEMPTS (default: 3)
- **Event-Driven Architecture**: Stop hook provides definitive completion signals
- **External State Machine**: Implementation_Plan.md provides durable, recoverable state

## Prerequisites

- Python 3.9 or higher
- Claude Code CLI installed and configured
- Git (optional, for version control)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Claude_Development_Loop
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install pytz pytest
```

3. Configure the MCP server path in your Claude Code configuration:
```json
{
  "mcpServers": {
    "automation": {
      "command": "python",
      "args": ["/path/to/Claude_Development_Loop/status_mcp_server.py"]
    }
  }
}
```

4. Set up the Stop hook in `.claude/settings.local.json`:
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

## Usage

### Starting the Automation

Run the orchestrator script to begin automated development:

```bash
python automate_dev.py
```

The orchestrator will:
1. Check for prerequisite files (`Implementation_Plan.md`, `CLAUDE.md`, `PRD.md`)
2. Execute tasks from the Implementation Plan using TDD methodology
3. Handle validation failures and retry logic automatically
4. Perform refactoring when all tasks are complete
5. Create comprehensive logs in `.claude/logs/`

### Custom Slash Commands

The system uses custom slash commands for different phases:

- `/continue` - Implement next task from Implementation_Plan.md using TDD
- `/validate` - Run tests and quality checks, report status
- `/update` - Mark current task complete (only after validation)
- `/correct` - Fix validation failures based on error details
- `/checkin` - Comprehensive project review and requirements verification
- `/refactor` - Identify refactoring opportunities
- `/finalize` - Implement refactoring tasks

### TDD Workflow

The system follows a strict TDD approach with specialized agents:

1. **Red Phase**: `test-writer` agent creates one failing test at a time
2. **Green Phase**: `implementation-verifier` agent writes minimal passing code
3. **Refactor Phase**: `refactoring-specialist` agent improves code quality

### Creating an Implementation Plan

Create an `Implementation_Plan.md` file with your project tasks:

```markdown
# Implementation Plan

## Phase 1: Core Features
- [ ] Task 1.1: Implement user authentication
- [ ] Task 1.2: Create database models
- [ ] Task 1.3: Build REST API endpoints

## Phase 2: Additional Features
- [ ] Task 2.1: Add email notifications
- [ ] Task 2.2: Implement file uploads
```

Tasks marked with `[ ]` are incomplete and will be executed sequentially.

## Project Structure

```
Claude_Development_Loop/
├── automate_dev.py              # Main orchestrator script
├── status_mcp_server.py         # MCP server for status reporting
├── Implementation_Plan.md       # Task checklist (state management)
├── CLAUDE.md                   # Project instructions for Claude
├── requirements.txt            # Python dependencies
├── tests/                      # Test suite
│   ├── test_orchestrator.py   # Orchestrator tests
│   └── test_mcp_server.py     # MCP server tests
├── reference/                  # Reference documentation
│   ├── agents/                # Agent descriptions
│   ├── commands/              # Command templates
│   └── settings.json          # Configuration examples
└── .claude/                   # Runtime directory (created automatically)
    ├── logs/                  # Timestamped log files
    ├── commands/              # Custom slash commands
    └── signal_task_complete   # Completion signal file
```

## Logging

The system creates comprehensive logs in `.claude/logs/` with module-specific loggers:

- `orchestrator`: Main workflow events
- `task_tracker`: Task processing and failure tracking
- `command_executor`: Claude CLI command execution
- `validation`: Prerequisites and validation checks
- `error_handler`: Error scenarios and retry logic
- `usage_limit`: Usage limit detection and handling

Log files are timestamped: `orchestrator_YYYYMMDD_HHMMSS.log`

## Testing

Run the test suite to verify functionality:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_orchestrator.py

# Run with coverage report
pytest tests/ --cov=. --cov-report=html
```

## Error Handling

The system includes robust error handling:

- **Circuit Breaker**: Maximum 3 fix attempts per task before manual intervention
- **Usage Limit Recovery**: Automatic retry after Claude API limits reset
- **Graceful Degradation**: Continues with remaining tasks on permanent failures
- **Comprehensive Logging**: All errors logged with context for debugging

## Development

### Adding New Tests

Tests follow TDD methodology with clear Given/When/Then structure:

```python
def test_new_functionality():
    """
    Test that new functionality works correctly.
    
    Given: Initial conditions
    When: Action is performed
    Then: Expected outcome occurs
    """
    # Test implementation
```

### Extending the Orchestrator

To add new functionality:

1. Write a failing test in `tests/test_orchestrator.py`
2. Implement minimal code to pass the test
3. Refactor for code quality
4. Update documentation

## Contributing

Contributions are welcome! Please follow the TDD methodology and ensure all tests pass before submitting changes.

## License

[Specify your license here]

## Support

For issues or questions, please create an issue in the project repository.

## Acknowledgments

Built for use with Claude Code CLI by Anthropic.