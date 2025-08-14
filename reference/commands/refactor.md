## Objective
Review this project and surface all opportunities for refactoring. Your examination must be systematic and thorough. Our goal with refactoring is to improve code quality without breaking any functionality or causing any of our test suite to fail.

## Primary Goals
- Improve code readability and maintainability
- Reduce code duplication
- Better organize the file/folder structure
- Standardize naming conventions
- Simplify complex functions and classes
- Identify content that should be removed or consolidated (such as old status files, temporary unused scripts, etc).

## Critical Files to Preserve
**DO NOT modify or delete:**
- Claude.md (or any .md files containing project documentation)
- README.md
- LICENSE files
- .gitignore
- Package files (package.json, requirements.txt, go.mod, Cargo.toml, etc.)
- Configuration files (.env, .env.example, config files)
- GitHub workflows (.github directory)
- Docker files (Dockerfile, docker-compose.yml)
- Implementation Plan documents
- .leann directory and files

## Claude Code Specific Instructions
- Your job is to identify the opportunities and problems and then create a plan for solving the issues that you found and implementing the opportunities that you identified.
- Once you've created a plan, add additional phases and tasks to our Implementation Plan document that cover your plan.
- A separate Agent will actually implement your plan based on the phases and tasks that you add to our Implementation Plan document.

TOOLS AVAILABLE:

- Web Search (search the web for answers)
- Context7 (search for coding guidelines and samples)
- LEANN (semantic search of current project structure and project documentation)

## Constraints
**DO NOT:**
- Change any external behavior or functionality
- Remove or modify any documentation (inline comments, docstrings, markdown files)
- Delete test files or test cases
- Break any existing APIs or interfaces
- Remove any files without explicit confirmation
- Make changes that would break imports in other files without updating them

## Specific Tasks
1. Identify repeated code that can be broken down into reusable functions/modules
2. Identify opportunities to break down functions longer than 20-30 lines into smaller, focused functions
3. Identify opportunities to rename variables and functions to be more descriptive
4. Identify opportunities to group related functionality into appropriate modules/classes
5. Identify opportunities to remove unused imports and dead code (but list them first for confirmation)
6. Identify opportunities to ensure consistent code formatting throughout
7. Identify opportunities to add type hints where missing (if applicable to the language)
8. Identify opportunities to enhance or bring our UI and UX into alignment with our overall theme and design choices
9. Look for issues related to design. Do we have an attractive design? Is it consistent throughout our project? Are we following good design principles? Does our design appear professional?
10. Look for performance bottlenecks and create tasks for any issues that you find. Make sure that from a performance perspective we are aligned with other professional Apps and that we do not have any outstanding performance related issues.

## Working Approach
- Start by analyzing the project structure with `find` or `tree` commands
- Read the Claude.md file first to understand project-specific conventions
- Create a refactoring plan
- Test frequently if the project has a test suite
- If no tests exist, manually verify critical functionality