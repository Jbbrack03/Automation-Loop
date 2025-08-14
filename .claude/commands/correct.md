# /correct

Fix validation failures using the provided error details.

## Arguments

Receives error details as an argument from the orchestrator, typically containing:
- Test failure messages
- Linting issues
- Type checking errors
- Stack traces and error locations

## Process

1. **Analyze Errors**: Parse the provided error details to understand failures
2. **Identify Root Causes**: Determine why tests are failing or checks are not passing
3. **Apply Fixes**:
   - Fix failing tests by correcting implementation code
   - Address linting issues (formatting, style violations)
   - Resolve type checking errors
   - Handle any import or dependency issues
4. **Verify Fixes**: Run the specific failing tests locally to confirm fixes
5. **Report Status**: Call `report_status` MCP tool with:
   - `status: "correction_attempted"`
   - Details about what was fixed
   - Any issues that couldn't be resolved

## Requirements

- Focus on fixing actual bugs, not modifying tests to pass
- Maintain existing functionality while fixing issues
- Preserve test coverage and quality standards
- Document any workarounds or temporary fixes

## Error Priority

1. **Test Failures** (highest priority)
2. **Type Errors** (can break runtime)
3. **Linting Issues** (code quality)

## Status Reporting

```json
{
  "status": "correction_attempted",
  "details": {
    "fixes_applied": [<list of fixes>],
    "issues_resolved": <count>,
    "issues_remaining": <count>,
    "unable_to_fix": [<list of unresolvable issues>]
  },
  "task_description": "Attempted correction of validation failures"
}
```