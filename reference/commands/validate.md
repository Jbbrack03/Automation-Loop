Perform intelligent TDD validation based on the type of work completed during this session.

## Session Type Detection & Validation Rules:

### Code Implementation Sessions
**When**: New features, bug fixes with code changes, significant refactoring
**Requirements**:
1. Tests were written and executed recently
2. All tests are currently passing
3. No tests are improperly skipped
4. Implementation for this session followed TDD Red-Green-Refactor cycle
5. New functionality has corresponding test coverage that was implemented according to TDD
6. Tests were written correctly, and not adjusted to just make the implementation pass. Our tests should be written first, using our tools as resources to ensure that they are correct. A test should ONLY be modified if you have high confidence that the test is truly incorrect. Otherwise it is a violation of TDD to modify a test just to make implementation pass (as in taking shortcuts or avoiding a problem). It is not a violation of TDD to correct a test that is truly incorrect. If you are unsure if a test was written correctly, use tools such as context7 and web search to research. Continue until you have high confidence that you understand how the test should be written.
7. If applicable to our project language and architecture, all linting and/or typescript errors must have been corrected according to best practices.
8. If you find errors or issues related to work from previous phases, then validation should fail. Our goal is to move forward with a completely clean project.
9. Use zen MCP Server to audit our codebase to surface any issues that may exist. Validate Zen's findings before adding the issues found to our implementation plan.

### Documentation/Configuration Sessions  
**When**: Only .md, .txt, README, config files, or comments were modified
**Requirements**:
1. Changes improve project clarity and maintainability
2. No broken links or formatting issues
3. Technical accuracy of documentation

### Bug Fix Sessions
**When**: Fixing existing functionality without adding new features
**Requirements**:
1. Tests were executed to verify fix
2. All tests pass including tests from previous phases and work sessions
3. No regression in existing functionality

### Refactoring Sessions
**When**: Code structure improvements without behavior changes
**Requirements**:
1. All existing tests still pass
2. Tests were executed to verify no regressions
3. Code quality improved without changing functionality

## Test Modification Policy:
- **NEVER** modify tests just to make implementation pass
- **ONLY** modify tests when genuinely incorrect after research
- **MUST** use context7 and web search to verify test correctness before modification
- **MUST** document reasoning when modifying tests