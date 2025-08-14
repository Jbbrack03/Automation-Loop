## Objective
Our refactoring research process has identified refactoring opportunities in our project. These issues and opportunities have been added to our Implementation Plan document as tasks for you to complete. Locate and read our Implementation Plan document and Claude.md and then check and optimize CLAUDE.md if needed. Use semantic search through LEANN MCP to review recent progress. Focus on the next highest priority task or feature that needs to be developed.

## CRITICAL: CLAUDE.md Size Management

**FIRST STEP - Check CLAUDE.md file size:**
1. Check if CLAUDE.md exists and measure its size in characters
2. **If CLAUDE.md > 40,000 characters:** Archive older content before continuing

**Archiving Process:**
1. Create or append to `CLAUDE_ARCHIVE.md` 
2. Move implementation history older than 30 days to the archive
3. **Keep in CLAUDE.md:**
   - Project overview and architecture
   - **TDD rules and methodology definitions** (critical for development standards)
   - Development process rules, coding standards, and quality guidelines
   - Project-specific rules and constraints
   - Current development status and recent updates (last 30 days)
   - All development commands and file structure
   - Recent implementation notes and current todo items
   - Active technology stack and conventions
4. **Move to CLAUDE_ARCHIVE.md:**
   - Detailed implementation history older than 30 days
   - Completed phase documentation
   - Old status updates and completed milestones
5. Ensure CLAUDE.md remains under 40,000 characters
6. Add a note in CLAUDE.md referencing the archive: "Older implementation history moved to CLAUDE_ARCHIVE.md"

**If CLAUDE.md is already ≤ 40,000 characters:** Continue with normal development

## Sub Agent Usage when Implementing new features following strict Red-Green-Refactor:

You should act as the Orchestrator in our multi-agent TDD system. Within this system, we proceed through our TDD cycle one test at a time. Our TDD sub agent team is made up of test-writer, implementation verifier, and refactoring-specialist. Review Claude.md and our Implementation Plan documentation to determine the next task in our project. Once you've identified the next task:

1. Use test-writer to create the next failing test according to our Implementation Plan
2. Use implementation-verifier to write minimal passing code to pass the most recent failing test
3. Use refactoring-specialist to improve the code from the most recently written test and implementation

Once this cycle has been completed, determine if there is enough room in your context window to assign another cycle to the TDD sub agent team. If there is enough room in your context window, then select the next task from our Implementation Plan and begin the Red-Green-Refactor cycle again. Continue in this pattern until you near the end of your context window.

## Development Process

Review the current state of the project and follow strict TDD for this session. Tests should be written one at a time. The next test should not be written until the previous task has completed the Red-Green-Refactor cycle. Work until you have completed a meaningful unit of work.