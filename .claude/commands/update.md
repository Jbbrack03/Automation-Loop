# /update

Mark the current task as complete in Implementation_Plan.md and report project status.

## Process

1. **Update Task State**: 
   - Read `Implementation_Plan.md`
   - Find the current task (first incomplete task marked with `[ ]`)
   - Change its marker to `[X]` to indicate completion
   - Save the updated file

2. **Check Project Status**:
   - Scan the entire `Implementation_Plan.md` for remaining incomplete tasks
   - Determine if the project is complete or has remaining work

3. **Report Status**: **MUST** call the `report_status` MCP tool with:
   - If tasks remain: `status: "project_incomplete"`
   - If all complete: `status: "project_complete"`
   - Include count of completed and remaining tasks in `details`
   - Include the description of the task just completed

## Requirements

- Only mark tasks complete after successful validation
- Preserve the exact formatting of Implementation_Plan.md
- Never mark multiple tasks complete at once
- Maintain task hierarchy and indentation

## Status Reporting Structure

```json
{
  "status": "project_complete" | "project_incomplete",
  "details": {
    "completed_task": "<description of task just marked complete>",
    "total_tasks": <count>,
    "completed_tasks": <count>,
    "remaining_tasks": <count>,
    "next_task": "<description of next task>" | null
  },
  "task_description": "Updated task state in Implementation_Plan.md"
}
```