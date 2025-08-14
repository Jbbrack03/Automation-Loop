# /refactor

Analyze the codebase for refactoring opportunities and report findings.

## Process

1. **Code Analysis**:
   - Identify code duplication across files
   - Find overly complex functions (high cyclomatic complexity)
   - Detect violated SOLID principles
   - Locate tight coupling between modules
   - Find magic numbers and hardcoded values
   - Identify missing abstractions

2. **Pattern Recognition**:
   - Repeated code blocks that could be extracted
   - Similar functions that could be generalized
   - Common patterns that could use design patterns
   - Inconsistent naming or style

3. **Priority Assessment**:
   - **High Priority**: Bugs waiting to happen, severe duplication
   - **Medium Priority**: Maintainability issues, moderate complexity
   - **Low Priority**: Style improvements, minor optimizations

4. **Report Status**: **MUST** call the `report_status` MCP tool with:
   - If refactoring needed: `status: "refactoring_needed"`
   - If code is clean: `status: "no_refactoring_needed"`
   - Include detailed list of refactoring opportunities
   - Provide effort estimates for each item

## Requirements

- Focus on meaningful improvements, not perfectionism
- Consider cost/benefit of each refactoring
- Ensure refactoring won't break existing functionality
- Maintain backward compatibility where needed
- Keep refactoring suggestions actionable and specific

## Refactoring Categories

1. **Extract Method**: Long functions that do multiple things
2. **Extract Class**: Classes with too many responsibilities
3. **Remove Duplication**: Repeated code blocks
4. **Simplify Conditionals**: Complex if/else chains
5. **Introduce Constants**: Replace magic numbers
6. **Improve Naming**: Unclear variable/function names

## Status Reporting Structure

```json
{
  "status": "refactoring_needed" | "no_refactoring_needed",
  "details": {
    "opportunities": [
      {
        "type": "extract_method" | "remove_duplication" | etc,
        "location": "<file:line>",
        "description": "<what to refactor>",
        "priority": "high" | "medium" | "low",
        "effort": "small" | "medium" | "large"
      }
    ],
    "total_opportunities": <count>,
    "high_priority_count": <count>,
    "estimated_total_effort": "<time estimate>"
  },
  "task_description": "Codebase refactoring analysis"
}
```