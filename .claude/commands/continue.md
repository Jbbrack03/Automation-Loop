# /continue

Implement the next task from Implementation_Plan.md using Test-Driven Development (TDD).

## Process

1. **Read State**: Parse `Implementation_Plan.md` to identify the next incomplete task (marked with `[ ]`)
2. **TDD Implementation**:
   - **Red Phase**: Write a failing test for the functionality
   - **Green Phase**: Write minimal code to make the test pass
   - **Refactor Phase**: Improve code quality while keeping tests green
3. **Status Reporting**: Call the `report_status` MCP tool with:
   - `status: "task_started"` when beginning
   - `status: "task_completed"` when done
   - Include task description and any relevant details

## Requirements

- Follow strict TDD methodology - test first, then implement
- Write comprehensive tests that cover edge cases
- Keep implementations minimal to pass tests
- Refactor for clarity and maintainability
- Document significant design decisions

## Error Handling

If no tasks remain incomplete:
- Call `report_status` with `status: "project_complete"`
- Provide summary of all completed tasks