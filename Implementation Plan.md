\# \*\*Implementation Plan: Automated Claude Code Development Workflow\*\*

\*\*Project:\*\* Architecting a Resilient, Automated Development Loop with Claude Code  
\*\*Development Methodology:\*\* Test-Driven Development (TDD)  
\*\*Target Executor:\*\* AI Coding Agent

\#\# \*\*Overview\*\*

This document provides a detailed, step-by-step plan to implement the automated development workflow as specified in the "Architecting a Resilient, Automated Development Loop with Claude Code" PRD. Each phase and task is designed to be executed sequentially by an AI coding agent. The TDD approach ensures that for every piece of functionality, a failing test is written first, followed by the implementation code to make the test pass.

\---

\#\# \*\*Phase 0: Project Initialization and Prerequisite Setup\*\*

\*\*Goal:\*\* Create the basic project structure, initialize version control, and establish the initial set of required files.

\* \*\*Task 0.1: Create Project Directory Structure\*\*  
    \* Create the root project directory.  
    \* Inside the root, create the following subdirectories:  
        \* \`.claude/commands/\`  
        \* \`tests/\`

\* \*\*Task 0.2: Initialize Git Repository\*\*  
    \* Initialize a new Git repository in the root directory.  
    \* Create a \`.gitignore\` file and add common Python patterns, IDE files, and the \`.claude/\` directory (except for the \`commands\` subdirectory). It should include:  
        \`\`\`  
        \_\_pycache\_\_/  
        \*.pyc  
        .env  
        .vscode/  
        .idea/  
        .claude/logs/  
        .claude/signal\_task\_complete  
        .claude/status\_\*.json  
        .claude/settings.local.json  
        \`\`\`

\* \*\*Task 0.3: Create Placeholder Project Files\*\*  
    \* Create an empty file named \`PRD.md\` in the root directory.  
    \* Create a file named \`Implementation\_Plan.md\` in the root directory. This file will serve as the state manager. Populate it with the following initial content:  
        \`\`\`markdown  
        \# Project Implementation Plan  
        \- \[ \] Phase 1: Setup authentication system  
        \- \[ \] Phase 2: Create database models  
        \`\`\`

\* \*\*Task 0.4: Install Python Dependencies\*\*  
    \* Install the \`pytz\` and \`pytest\` libraries.  
    \* Create a \`requirements.txt\` file listing the dependencies:  
        \`\`\`  
        pytz  
        pytest  
        \`\`\`

\* \*\*Task 0.5: Initial Git Commit\*\*  
    \* Stage all the newly created files and directories.  
    \* Make the initial commit with the message: \`feat: initial project structure and setup\`.

\---

\#\# \*\*Phase 1: Core Orchestrator Scaffolding (TDD)\*\*

\*\*Goal:\*\* Create the main orchestrator script and implement the initial prerequisite checks.

\* \*\*Task 1.1: Create Initial Test File\*\*  
    \* In the \`tests/\` directory, create a new file named \`test\_orchestrator.py\`.

\* \*\*Task 1.2: Write Failing Test for Script Execution\*\*  
    \* In \`test\_orchestrator.py\`, write a \`pytest\` test that attempts to import the \`main\` function from \`automate\_dev.py\` and checks that the script is executable. This test will fail because the file doesn't exist yet.

\* \*\*Task 1.3: Create the Orchestrator Script\*\*  
    \* Create the \`automate\_dev.py\` file in the root directory.  
    \* Define an empty \`main()\` function and a standard \`if \_\_name\_\_ \== "\_\_main\_\_":\` block to call it.  
    \* Run the test from Task 1.2 to confirm it now passes.

\* \*\*Task 1.4: Write Failing Test for Prerequisite File Checks\*\*  
    \* In \`test\_orchestrator.py\`, write a test that checks if the orchestrator exits gracefully with an error if \`Implementation\_Plan.md\` is missing.  
    \* Write another test that checks for a warning if \`PRD.md\` or \`CLAUDE.md\` is missing.

\* \*\*Task 1.5: Implement Prerequisite Checks\*\*  
    \* In \`automate\_dev.py\`, add logic at the beginning of the \`main()\` function to check for the existence of \`Implementation\_Plan.md\`. If it's missing, print an error message and exit.  
    \* Add logic to check for \`PRD.md\` or \`CLAUDE.md\` and print a warning if neither is found.  
    \* Run the tests from Task 1.4 to confirm they pass.

\* \*\*Task 1.6: Commit Changes\*\*  
    \* Stage \`automate\_dev.py\` and \`tests/test\_orchestrator.py\`.  
    \* Commit with the message: \`feat: implement orchestrator scaffolding and prerequisite checks\`.

\---

\#\# \*\*Phase 2: State Management (\`TaskTracker\` Class)\*\*

\*\*Goal:\*\* Implement the class responsible for reading the \`Implementation\_Plan.md\` and tracking task state.

\* \*\*Task 2.1: Write Failing Tests for \`get\_next\_task\`\*\*  
    \* In \`test\_orchestrator.py\`, write tests for the \`TaskTracker\` class (which doesn't exist yet).  
    \* Test case 1: It correctly identifies the first incomplete task (\`\[ \]\`).  
    \* Test case 2: It returns \`(None, True)\` when all tasks are complete (\`\[X\]\`).  
    \* Test case 3: It returns \`(None, True)\` if the \`Implementation\_Plan.md\` file does not exist.

\* \*\*Task 2.2: Implement \`TaskTracker\` and \`get\_next\_task\`\*\*  
    \* In \`automate\_dev.py\`, create the \`TaskTracker\` class.  
    \* Implement the \`get\_next\_task\` method according to the logic in the PRD.  
    \* Run the tests from Task 2.1 to confirm they pass.

\* \*\*Task 2.3: Write Failing Tests for Failure Tracking\*\*  
    \* In \`test\_orchestrator.py\`, write tests for the failure tracking methods of \`TaskTracker\`.  
    \* Test case 1: \`increment\_fix\_attempts\` correctly increments the count for a task.  
    \* Test case 2: \`increment\_fix\_attempts\` returns \`False\` when \`MAX\_FIX\_ATTEMPTS\` is reached.  
    \* Test case 3: \`reset\_fix\_attempts\` removes a task from the tracking dictionary.

\* \*\*Task 2.4: Implement Failure Tracking Logic\*\*  
    \* In \`automate\_dev.py\`, add the \`fix\_attempts\` dictionary and the \`MAX\_FIX\_ATTEMPTS\` constant.  
    \* Implement the \`increment\_fix\_attempts\` and \`reset\_fix\_attempts\` methods.  
    \* Run the tests from Task 2.3 to confirm they pass.

\* \*\*Task 2.5: Commit Changes\*\*  
    \* Commit with the message: \`feat: implement TaskTracker for state management and failure tracking\`.

\---

\#\# \*\*Phase 3: Claude Command Execution and Signal Handling\*\*

\*\*Goal:\*\* Implement the function to run Claude commands and reliably detect their completion.

\* \*\*Task 3.1: Write Failing Test for \`run\_claude\_command\`\*\*  
    \* In \`test\_orchestrator.py\`, write a test that mocks the \`subprocess.run\` call and verifies that \`run\_claude\_command\` constructs the correct Claude CLI command array, including the \`--output-format json\` and \`--dangerously-skip-permissions\` flags.

\* \*\*Task 3.2: Implement \`run\_claude\_command\`\*\*  
    \* In \`automate\_dev.py\`, implement the \`run\_claude\_command\` function as detailed in the PRD. It should take a slash command and arguments, execute it via \`subprocess.run\`, and parse the JSON output. For now, it does not need the signal file logic.  
    \* Run the test from Task 3.1 to confirm it passes.

\* \*\*Task 3.3: Write Failing Test for Signal File Logic\*\*  
    \* In \`test\_orchestrator.py\`, write a test that verifies \`run\_claude\_command\` waits for the \`signal\_task\_complete\` file to exist before returning and cleans it up afterward. You will need to mock \`os.path.exists\` and \`os.remove\`.

\* \*\*Task 3.4: Implement Signal File Waiting Logic\*\*  
    \* In \`automate\_dev.py\`, add the \`while not os.path.exists(SIGNAL\_FILE)\` loop inside \`run\_claude\_command\`.  
    \* Ensure the signal file is removed after the loop breaks.  
    \* Run the test from Task 3.3 to confirm it passes.

\* \*\*Task 3.5: Commit Changes\*\*  
    \* Commit with the message: \`feat: implement claude command execution with reliable signal handling\`.

\---

\#\# \*\*Phase 4: MCP Server for Reliable Status Reporting\*\*

\*\*Goal:\*\* Create the MCP server for structured status reporting and the orchestrator logic to consume it.

\* \*\*Task 4.1: Create MCP Server Test File\*\*  
    \* In the \`tests/\` directory, create a file named \`test\_mcp\_server.py\`.

\* \*\*Task 4.2: Write Failing Test for \`report\_status\` Tool\*\*  
    \* In \`test\_mcp\_server.py\`, write a test that instantiates the \`StatusServer\` and calls the \`report\_status\` tool. It should verify that a correctly formatted, timestamped JSON file is created in the \`.claude/\` directory.

\* \*\*Task 4.3: Implement the MCP Server\*\*  
    \* Create the \`status\_mcp\_server.py\` file in the root directory.  
    \* Implement the \`StatusServer\` class and the \`@Tool() def report\_status(...)\` method exactly as specified in the PRD.  
    \* Run the test from Task 4.2 to confirm it passes.

\* \*\*Task 4.4: Write Failing Test for \`get\_latest\_status\`\*\*  
    \* In \`test\_orchestrator.py\`, write a test for the \`get\_latest\_status\` function. It should:  
        \* Create multiple dummy \`status\_\*.json\` files with different timestamps.  
        \* Verify that the function reads the content of the \*newest\* file.  
        \* Verify that \*all\* status files are deleted after reading.

\* \*\*Task 4.5: Implement \`get\_latest\_status\`\*\*  
    \* In \`automate\_dev.py\`, implement the \`get\_latest\_status\` function as specified in the PRD.  
    \* Run the test from Task 4.4 to confirm it passes.

\* \*\*Task 4.6: Commit Changes\*\*  
    \* Stage \`status\_mcp\_server.py\` and \`tests/test\_mcp\_server.py\`.  
    \* Commit with the message: \`feat: implement MCP server for reliable status reporting\`.

\---

\#\# \*\*Phase 5: Custom Slash Commands\*\*

\*\*Goal:\*\* Create all the necessary slash command files in the \`.claude/commands/\` directory.

\* \*\*Task 5.1: Create \`/continue.md\`\*\*  
    \* Content should instruct the agent to read the next task from \`Implementation\_Plan.md\` and implement it using TDD.

\* \*\*Task 5.2: Create \`/validate.md\`\*\*  
    \* Content should instruct the agent to run all tests, linting, and type checks. Based on the outcome, it MUST call the \`report\_status\` MCP tool with either \`validation\_passed\` or \`validation\_failed\`.

\* \*\*Task 5.3: Create \`/update.md\`\*\*  
    \* Content should instruct the agent to mark the current task as complete (\`\[X\]\`) in \`Implementation\_Plan.md\` and then call the \`report\_status\` MCP tool to indicate if the project is complete or incomplete.

\* \*\*Task 5.4: Create \`/correct.md\`\*\*  
    \* Content should instruct the agent that the previous validation failed. It should use the provided error details (passed as an argument) to fix the code.

\* \*\*Task 5.5: Create \`/checkin.md\`\*\*  
    \* Content should instruct the agent to perform a full project review and add any new tasks to \`Implementation\_Plan.md\`. It must then call the \`report\_status\` MCP tool.

\* \*\*Task 5.6: Create \`/refactor.md\`\*\*  
    \* Content should instruct the agent to analyze the code for refactoring opportunities and call the \`report\_status\` MCP tool accordingly.

\* \*\*Task 5.7: Create \`/finalize.md\`\*\*  
    \* Content should instruct the agent to implement the refactoring tasks identified by \`/refactor\`.

\* \*\*Task 5.8: Commit Changes\*\*  
    \* Stage the entire \`.claude/commands/\` directory.  
    \* Commit with the message: \`feat: create all custom slash commands\`.

\---

\#\# \*\*Phase 6: Hook Configuration\*\*

\*\*Goal:\*\* Configure the \`Stop\` hook to enable the signal-based completion detection.

\* \*\*Task 6.1: Create Hook Configuration File\*\*  
    \* Create the file \`.claude/settings.local.json\`.

\* \*\*Task 6.2: Add Stop Hook Configuration\*\*  
    \* Add the JSON configuration for the \`Stop\` hook as specified in the PRD, which executes \`touch .claude/signal\_task\_complete\`.

\* \*\*Task 6.3: Commit Changes\*\*  
    \* Commit with the message: \`feat: configure Stop hook for reliable completion signaling\`.

\---

\#\# \*\*Phase 7: Main Orchestration Loop\*\*

\*\*Goal:\*\* Implement the primary TDD loop in the orchestrator script.

\* \*\*Task 7.1: Write Failing Test for Main Loop (Happy Path)\*\*  
    \* In \`test\_orchestrator.py\`, write a high-level test that mocks \`run\_claude\_command\` and \`get\_latest\_status\`.  
    \* Verify that the main loop correctly calls \`/clear\`, \`/continue\`, \`/validate\`, and \`/update\` in sequence when validation passes.

\* \*\*Task 7.2: Implement Main Loop (Happy Path)\*\*  
    \* In \`automate\_dev.py\`, build the \`while\` loop inside the \`main\` function.  
    \* Implement the sequence of calls for the happy path.  
    \* Run the test from Task 7.1 to confirm it passes.

\* \*\*Task 7.3: Write Failing Test for Correction Path\*\*  
    \* In \`test\_orchestrator.py\`, write a test where \`get\_latest\_status\` returns \`validation\_failed\`.  
    \* Verify that the orchestrator then calls \`/correct\` and that the \`TaskTracker\`'s \`increment\_fix\_attempts\` method is called.  
    \* Verify that the loop breaks if max fix attempts are exceeded.

\* \*\*Task 7.4: Implement Correction Path\*\*  
    \* In \`automate\_dev.py\`, add the \`if validation\_status \== "validation\_failed":\` block.  
    \* Implement the logic to handle failures, including calling \`/correct\` and interacting with the \`TaskTracker\`.  
    \* Run the test from Task 7.3 to confirm it passes.

\* \*\*Task 7.5: Commit Changes\*\*  
    \* Commit with the message: \`feat: implement main TDD orchestration loop with correction path\`.

\---

\#\# \*\*Phase 8: Refactoring and Finalization Loop\*\*

\*\*Goal:\*\* Implement the end-of-project refactoring logic.

\* \*\*Task 8.1: Write Failing Test for Refactoring Loop\*\*  
    \* In \`test\_orchestrator.py\`, write a test for when \`get\_latest\_status\` after \`/update\` returns \`project\_complete\`.  
    \* Verify that the code then enters a new loop that calls \`/checkin\`, \`/refactor\`, and \`/finalize\` in the correct sequence based on the status returned.  
    \* Verify the loop terminates when status is \`no\_refactoring\_needed\`.

\* \*\*Task 8.2: Implement Refactoring Loop\*\*  
    \* In \`automate\_dev.py\`, add the logic to handle the \`project\_complete\` status, triggering the refactoring and finalization loop as described in the PRD.  
    \* Run the test from Task 8.1 to confirm it passes.

\* \*\*Task 8.3: Commit Changes\*\*  
    \* Commit with the message: \`feat: implement end-of-project refactoring and finalization loop\`.

\---

\#\# \*\*Phase 9: Usage Limit Handling\*\*

\*\*Goal:\*\* Make the orchestrator resilient to Claude Max API usage limits.

\* \*\*Task 9.1: Write Failing Tests for Usage Limit Parsing\*\*  
    \* In \`test\_orchestrator.py\`, write tests for the \`parse\_usage\_limit\_error\` function.  
    \* Include test cases for both the natural language time format (e.g., "7pm (America/Chicago)") and the Unix timestamp format.  
    \* Also test the \`calculate\_wait\_time\` helper function.

\* \*\*Task 9.2: Implement Usage Limit Functions\*\*  
    \* In \`automate\_dev.py\`, implement the \`parse\_usage\_limit\_error\`, \`calculate\_wait\_time\`, and \`handle\_usage\_limit\` functions exactly as specified in the PRD.  
    \* Run the tests from Task 9.1 to confirm they pass.

\* \*\*Task 9.3: Integrate Usage Limit Handling\*\*  
    \* In \`automate\_dev.py\`, modify the \`run\_claude\_command\` function to check the captured output for the usage limit error string. If found, it should call the handler and retry the command.  
    \* Write a test to verify this retry behavior.

\* \*\*Task 9.4: Commit Changes\*\*  
    \* Commit with the message: \`feat: implement automatic recovery from Claude usage limits\`.

\---

\#\# \*\*Phase 10: Logging and Final Polish\*\*

\*\*Goal:\*\* Add comprehensive logging and finalize the project.

\* \*\*Task 10.1: Write Test for Logging\*\*  
    \* In \`test\_orchestrator.py\`, write a test to ensure that after running the orchestrator, a log file is created in the \`.claude/logs/\` directory.

\* \*\*Task 10.2: Implement Logging\*\*  
    \* In \`automate\_dev.py\`, add the \`setup\_logging\` function and integrate the \`loggers\` dictionary throughout the script as detailed in the PRD.  
    \* Run the test from Task 10.1 to confirm it passes.

\* \*\*Task 10.3: Final Code Review\*\*  
    \* Review all code files (\`automate\_dev.py\`, \`status\_mcp\_server.py\`, tests, and slash commands) for clarity, comments, and adherence to the PRD. Refine as needed.

\* \*\*Task 10.4: Create Project \`README.md\`\*\*  
    \* Create a \`README.md\` in the root directory.  
    \* Explain the project's purpose, how to set it up (install dependencies, configure MCP server path), and how to run the automation using \`python automate\_dev.py\`.

\* \*\*Task 10.5: Final Commit\*\*  
    \* Stage all final changes.  
    \* Commit with the message: \`docs: add README and finalize logging and code comments\`.

