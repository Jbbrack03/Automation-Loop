# /checkin

Perform a comprehensive project review and update Implementation_Plan.md with any new tasks discovered.

## Process

1. **Project Review**:
   - Analyze all source files for completeness
   - Check test coverage and identify gaps
   - Review documentation status
   - Verify all requirements from PRD.md or CLAUDE.md are addressed
   - Identify missing features or functionality

2. **Code Quality Assessment**:
   - Check for code smells and anti-patterns
   - Identify areas needing refactoring
   - Review error handling completeness
   - Assess logging and debugging capabilities

3. **Update Implementation Plan**:
   - Add any newly discovered tasks to `Implementation_Plan.md`
   - Organize tasks by priority and dependencies
   - Mark any obsolete tasks for removal
   - Ensure task descriptions are clear and actionable

4. **Report Status**: **MUST** call the `report_status` MCP tool with:
   - `status: "checkin_complete"`
   - Summary of project health
   - List of new tasks added
   - Areas of concern identified

## Requirements

- Be thorough but avoid creating unnecessary tasks
- Focus on actual gaps, not nice-to-haves
- Maintain consistency with existing task format
- Prioritize tasks that block project completion

## Review Checklist

- [ ] All PRD requirements implemented
- [ ] Test coverage adequate (aim for >80%)
- [ ] Error handling comprehensive
- [ ] Documentation up to date
- [ ] No critical security issues
- [ ] Performance acceptable
- [ ] Code follows project conventions

## Status Reporting Structure

```json
{
  "status": "checkin_complete",
  "details": {
    "project_health": "good" | "needs_work" | "critical",
    "new_tasks_added": <count>,
    "coverage_percentage": <number>,
    "critical_issues": [<list>],
    "recommendations": [<list>]
  },
  "task_description": "Comprehensive project review and planning update"
}
```