# /finalize

Implement the refactoring tasks identified by the /refactor command.

## Process

1. **Read Refactoring List**:
   - Get the list of refactoring opportunities from previous analysis
   - Prioritize high-priority items first
   - Group related refactorings for efficiency

2. **Implement Refactorings**:
   - **Safety First**: Ensure all tests pass before starting
   - **One at a Time**: Apply refactorings incrementally
   - **Test After Each**: Run tests after each refactoring
   - **Commit Often**: Make atomic commits for each refactoring

3. **Refactoring Execution**:
   - Extract methods from long functions
   - Create abstractions for repeated code
   - Simplify complex conditionals
   - Replace magic numbers with named constants
   - Improve variable and function names
   - Apply appropriate design patterns

4. **Validation**:
   - Run full test suite after each change
   - Verify no functionality was broken
   - Check that code complexity decreased
   - Ensure code readability improved

5. **Report Status**: Call `report_status` MCP tool with:
   - `status: "finalization_complete"`
   - List of refactorings completed
   - Any refactorings skipped and why
   - Overall code quality improvement metrics

## Requirements

- Never break existing functionality
- Keep commits atomic and descriptive
- Document significant design changes
- Update tests if interfaces change
- Maintain backward compatibility

## Safety Rules

1. **Never refactor and add features simultaneously**
2. **Always have green tests before starting**
3. **Make one logical change at a time**
4. **If tests fail, revert immediately**
5. **Document why certain refactorings were skipped**

## Status Reporting Structure

```json
{
  "status": "finalization_complete",
  "details": {
    "refactorings_completed": [
      {
        "type": "<refactoring type>",
        "description": "<what was done>",
        "files_affected": [<list>],
        "tests_still_passing": true
      }
    ],
    "refactorings_skipped": [
      {
        "description": "<what was skipped>",
        "reason": "<why it was skipped>"
      }
    ],
    "total_completed": <count>,
    "total_skipped": <count>,
    "code_quality_improvement": "<assessment>"
  },
  "task_description": "Implementation of identified refactorings"
}
```