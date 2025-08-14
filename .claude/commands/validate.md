# /validate

Run all tests, linting, and type checks to validate the current implementation.

## Process

1. **Run Tests**: Execute `pytest tests/` to run all unit tests
2. **Check Linting**: Run appropriate linting tools if configured (e.g., `flake8`, `pylint`)
3. **Type Checking**: Run type checker if configured (e.g., `mypy`)
4. **Report Status**: Based on the outcome, **MUST** call the `report_status` MCP tool:
   - If all checks pass: `status: "validation_passed"`
   - If any check fails: `status: "validation_failed"`
   - Include detailed error messages and failure counts in `details`

## Requirements

- Run all validation checks even if early ones fail
- Capture and report all error messages
- Provide clear summary of what passed and what failed
- Include specific file locations and line numbers for failures

## Status Reporting Structure

```json
{
  "status": "validation_passed" | "validation_failed",
  "details": {
    "tests": {
      "passed": <count>,
      "failed": <count>,
      "errors": [<error messages>]
    },
    "linting": {
      "passed": <bool>,
      "issues": [<linting issues>]
    },
    "type_checking": {
      "passed": <bool>,
      "errors": [<type errors>]
    }
  },
  "task_description": "Validation of current implementation"
}
```