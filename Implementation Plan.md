# **Implementation Plan: Automated Claude Code Development Workflow**

**Project:** Architecting a Resilient, Automated Development Loop with Claude Code  
**Development Methodology:** Test-Driven Development (TDD)  
**Target Executor:** AI Coding Agent

## **Overview**

This document provides a detailed, step-by-step plan to implement the automated development workflow as specified in the "Architecting a Resilient, Automated Development Loop with Claude Code" PRD. Each phase and task is designed to be executed sequentially by an AI coding agent. The TDD approach ensures that for every piece of functionality, a failing test is written first, followed by the implementation code to make the test pass.

---

## **Phase 0: Project Initialization and Prerequisite Setup** ✅

**Goal:** Create the basic project structure, initialize version control, and establish the initial set of required files.

- [X] **Task 0.1: Create Project Directory Structure**
  - Create the root project directory.
  - Inside the root, create the following subdirectories:
    - `.claude/commands/`
    - `tests/`

- [X] **Task 0.2: Initialize Git Repository**
  - Initialize a new Git repository in the root directory.
  - Create a `.gitignore` file and add common Python patterns, IDE files, and the `.claude/` directory (except for the `commands` subdirectory). It should include:
    ```
    __pycache__/
    *.pyc
    .env
    .vscode/
    .idea/
    .claude/logs/
    .claude/signal_task_complete
    .claude/status_*.json
    .claude/settings.local.json
    ```

- [X] **Task 0.3: Create Placeholder Project Files**
  - Create an empty file named `PRD.md` in the root directory.
  - Create a file named `Implementation_Plan.md` in the root directory. This file will serve as the state manager. Populate it with the following initial content:
    ```markdown
    # Project Implementation Plan
    - [ ] Phase 1: Setup authentication system
    - [ ] Phase 2: Create database models
    ```

- [X] **Task 0.4: Install Python Dependencies**
  - Install the `pytz` and `pytest` libraries.
  - Create a `requirements.txt` file listing the dependencies:
    ```
    pytz
    pytest
    ```

- [X] **Task 0.5: Initial Git Commit**
  - Stage all the newly created files and directories.
  - Make the initial commit with the message: `feat: initial project structure and setup`.

---

## **Phase 1: Core Orchestrator Scaffolding (TDD)** ✅

**Goal:** Create the main orchestrator script and implement the initial prerequisite checks.

- [X] **Task 1.1: Create Initial Test File**
  - In the `tests/` directory, create a new file named `test_orchestrator.py`.

- [X] **Task 1.2: Write Failing Test for Script Execution**
  - In `test_orchestrator.py`, write a `pytest` test that attempts to import the `main` function from `automate_dev.py` and checks that the script is executable. This test will fail because the file doesn't exist yet.

- [X] **Task 1.3: Create the Orchestrator Script**
  - Create the `automate_dev.py` file in the root directory.
  - Define an empty `main()` function and a standard `if __name__ == "__main__":` block to call it.
  - Run the test from Task 1.2 to confirm it now passes.

- [X] **Task 1.4: Write Failing Test for Prerequisite File Checks**
  - In `test_orchestrator.py`, write a test that checks if the orchestrator exits gracefully with an error if `Implementation_Plan.md` is missing.
  - Write another test that checks for a warning if `PRD.md` or `CLAUDE.md` is missing.

- [X] **Task 1.5: Implement Prerequisite Checks**
  - In `automate_dev.py`, add logic at the beginning of the `main()` function to check for the existence of `Implementation_Plan.md`. If it's missing, print an error message and exit.
  - Add logic to check for `PRD.md` or `CLAUDE.md` and print a warning if neither is found.
  - Run the tests from Task 1.4 to confirm they pass.

- [X] **Task 1.6: Commit Changes**
  - Stage `automate_dev.py` and `tests/test_orchestrator.py`.
  - Commit with the message: `feat: implement orchestrator scaffolding and prerequisite checks`.

---

## **Phase 2: State Management (`TaskTracker` Class)** ✅

**Goal:** Implement the class responsible for reading the `Implementation_Plan.md` and tracking task state.

- [X] **Task 2.1: Write Failing Tests for `get_next_task`**
  - In `test_orchestrator.py`, write tests for the `TaskTracker` class (which doesn't exist yet).
  - Test case 1: It correctly identifies the first incomplete task (`[ ]`).
  - Test case 2: It returns `(None, True)` when all tasks are complete (`[X]`).
  - Test case 3: It returns `(None, True)` if the `Implementation_Plan.md` file does not exist.

- [X] **Task 2.2: Implement `TaskTracker` and `get_next_task`**
  - In `automate_dev.py`, create the `TaskTracker` class.
  - Implement the `get_next_task` method according to the logic in the PRD.
  - Run the tests from Task 2.1 to confirm they pass.

- [X] **Task 2.3: Write Failing Tests for Failure Tracking**
  - In `test_orchestrator.py`, write tests for the failure tracking methods of `TaskTracker`.
  - Test case 1: `increment_fix_attempts` correctly increments the count for a task.
  - Test case 2: `increment_fix_attempts` returns `False` when `MAX_FIX_ATTEMPTS` is reached.
  - Test case 3: `reset_fix_attempts` removes a task from the tracking dictionary.

- [X] **Task 2.4: Implement Failure Tracking Logic**
  - In `automate_dev.py`, add the `fix_attempts` dictionary and the `MAX_FIX_ATTEMPTS` constant.
  - Implement the `increment_fix_attempts` and `reset_fix_attempts` methods.
  - Run the tests from Task 2.3 to confirm they pass.

- [X] **Task 2.5: Commit Changes**
  - Commit with the message: `feat: implement TaskTracker for state management and failure tracking`.

---

## **Phase 3: Claude Command Execution and Signal Handling** ✅

**Goal:** Implement the function to run Claude commands and reliably detect their completion.

- [X] **Task 3.1: Write Failing Test for `run_claude_command`**
  - In `test_orchestrator.py`, write a test that mocks the `subprocess.run` call and verifies that `run_claude_command` constructs the correct Claude CLI command array, including the `--output-format json` and `--dangerously-skip-permissions` flags.

- [X] **Task 3.2: Implement `run_claude_command`**
  - In `automate_dev.py`, implement the `run_claude_command` function as detailed in the PRD. It should take a slash command and arguments, execute it via `subprocess.run`, and parse the JSON output. For now, it does not need the signal file logic.
  - Run the test from Task 3.1 to confirm it passes.

- [X] **Task 3.3: Write Failing Test for Signal File Logic**
  - In `test_orchestrator.py`, write a test that verifies `run_claude_command` waits for the `signal_task_complete` file to exist before returning and cleans it up afterward. You will need to mock `os.path.exists` and `os.remove`.

- [X] **Task 3.4: Implement Signal File Waiting Logic**
  - In `automate_dev.py`, add the `while not os.path.exists(SIGNAL_FILE)` loop inside `run_claude_command`.
  - Ensure the signal file is removed after the loop breaks.
  - Run the test from Task 3.3 to confirm it passes.

- [X] **Task 3.5: Commit Changes**
  - Commit with the message: `feat: implement claude command execution with reliable signal handling`.

---

## **Phase 4: MCP Server for Reliable Status Reporting** ✅

**Goal:** Create the MCP server for structured status reporting and the orchestrator logic to consume it.

- [X] **Task 4.1: Create MCP Server Test File**
  - In the `tests/` directory, create a file named `test_mcp_server.py`.

- [X] **Task 4.2: Write Failing Test for `report_status` Tool**
  - In `test_mcp_server.py`, write a test that instantiates the `StatusServer` and calls the `report_status` tool. It should verify that a correctly formatted, timestamped JSON file is created in the `.claude/` directory.

- [X] **Task 4.3: Implement the MCP Server**
  - Create the `status_mcp_server.py` file in the root directory.
  - Implement the `StatusServer` class and the `@Tool() def report_status(...)` method exactly as specified in the PRD.
  - Run the test from Task 4.2 to confirm it passes.

- [X] **Task 4.4: Write Failing Test for `get_latest_status`**
  - In `test_orchestrator.py`, write a test for the `get_latest_status` function. It should:
    - Create multiple dummy `status_*.json` files with different timestamps.
    - Verify that the function reads the content of the *newest* file.
    - Verify that *all* status files are deleted after reading.

- [X] **Task 4.5: Implement `get_latest_status`**
  - In `automate_dev.py`, implement the `get_latest_status` function as specified in the PRD.
  - Run the test from Task 4.4 to confirm it passes.

- [X] **Task 4.6: Commit Changes**
  - Stage `status_mcp_server.py` and `tests/test_mcp_server.py`.
  - Commit with the message: `feat: implement MCP server for reliable status reporting`.

---

## **Phase 5: Custom Slash Commands**

**Goal:** Create all the necessary slash command files in the `.claude/commands/` directory.

- [ ] **Task 5.1: Create `/continue.md`**
  - Content should instruct the agent to read the next task from `Implementation_Plan.md` and implement it using TDD.

- [ ] **Task 5.2: Create `/validate.md`**
  - Content should instruct the agent to run all tests, linting, and type checks. Based on the outcome, it MUST call the `report_status` MCP tool with either `validation_passed` or `validation_failed`.

- [ ] **Task 5.3: Create `/update.md`**
  - Content should instruct the agent to mark the current task as complete (`[X]`) in `Implementation_Plan.md` and then call the `report_status` MCP tool to indicate if the project is complete or incomplete.

- [ ] **Task 5.4: Create `/correct.md`**
  - Content should instruct the agent that the previous validation failed. It should use the provided error details (passed as an argument) to fix the code.

- [ ] **Task 5.5: Create `/checkin.md`**
  - Content should instruct the agent to perform a full project review and add any new tasks to `Implementation_Plan.md`. It must then call the `report_status` MCP tool.

- [ ] **Task 5.6: Create `/refactor.md`**
  - Content should instruct the agent to analyze the code for refactoring opportunities and call the `report_status` MCP tool accordingly.

- [ ] **Task 5.7: Create `/finalize.md`**
  - Content should instruct the agent to implement the refactoring tasks identified by `/refactor`.

- [ ] **Task 5.8: Commit Changes**
  - Stage the entire `.claude/commands/` directory.
  - Commit with the message: `feat: create all custom slash commands`.

---

## **Phase 6: Hook Configuration**

**Goal:** Configure the `Stop` hook to enable the signal-based completion detection.

- [ ] **Task 6.1: Create Hook Configuration File**
  - Create the file `.claude/settings.local.json`.

- [ ] **Task 6.2: Add Stop Hook Configuration**
  - Add the JSON configuration for the `Stop` hook as specified in the PRD, which executes `touch .claude/signal_task_complete`.

- [ ] **Task 6.3: Commit Changes**
  - Commit with the message: `feat: configure Stop hook for reliable completion signaling`.

---

## **Phase 7: Main Orchestration Loop**

**Goal:** Implement the primary TDD loop in the orchestrator script.

- [ ] **Task 7.1: Write Failing Test for Main Loop (Happy Path)**
  - In `test_orchestrator.py`, write a high-level test that mocks `run_claude_command` and `get_latest_status`.
  - Verify that the main loop correctly calls `/clear`, `/continue`, `/validate`, and `/update` in sequence when validation passes.

- [ ] **Task 7.2: Implement Main Loop (Happy Path)**
  - In `automate_dev.py`, build the `while` loop inside the `main` function.
  - Implement the sequence of calls for the happy path.
  - Run the test from Task 7.1 to confirm it passes.

- [ ] **Task 7.3: Write Failing Test for Correction Path**
  - In `test_orchestrator.py`, write a test where `get_latest_status` returns `validation_failed`.
  - Verify that the orchestrator then calls `/correct` and that the `TaskTracker`'s `increment_fix_attempts` method is called.
  - Verify that the loop breaks if max fix attempts are exceeded.

- [ ] **Task 7.4: Implement Correction Path**
  - In `automate_dev.py`, add the `if validation_status == "validation_failed":` block.
  - Implement the logic to handle failures, including calling `/correct` and interacting with the `TaskTracker`.
  - Run the test from Task 7.3 to confirm it passes.

- [ ] **Task 7.5: Commit Changes**
  - Commit with the message: `feat: implement main TDD orchestration loop with correction path`.

---

## **Phase 8: Refactoring and Finalization Loop**

**Goal:** Implement the end-of-project refactoring logic.

- [ ] **Task 8.1: Write Failing Test for Refactoring Loop**
  - In `test_orchestrator.py`, write a test for when `get_latest_status` after `/update` returns `project_complete`.
  - Verify that the code then enters a new loop that calls `/checkin`, `/refactor`, and `/finalize` in the correct sequence based on the status returned.
  - Verify the loop terminates when status is `no_refactoring_needed`.

- [ ] **Task 8.2: Implement Refactoring Loop**
  - In `automate_dev.py`, add the logic to handle the `project_complete` status, triggering the refactoring and finalization loop as described in the PRD.
  - Run the test from Task 8.1 to confirm it passes.

- [ ] **Task 8.3: Commit Changes**
  - Commit with the message: `feat: implement end-of-project refactoring and finalization loop`.

---

## **Phase 9: Usage Limit Handling**

**Goal:** Make the orchestrator resilient to Claude Max API usage limits.

- [ ] **Task 9.1: Write Failing Tests for Usage Limit Parsing**
  - In `test_orchestrator.py`, write tests for the `parse_usage_limit_error` function.
  - Include test cases for both the natural language time format (e.g., "7pm (America/Chicago)") and the Unix timestamp format.
  - Also test the `calculate_wait_time` helper function.

- [ ] **Task 9.2: Implement Usage Limit Functions**
  - In `automate_dev.py`, implement the `parse_usage_limit_error`, `calculate_wait_time`, and `handle_usage_limit` functions exactly as specified in the PRD.
  - Run the tests from Task 9.1 to confirm they pass.

- [ ] **Task 9.3: Integrate Usage Limit Handling**
  - In `automate_dev.py`, modify the `run_claude_command` function to check the captured output for the usage limit error string. If found, it should call the handler and retry the command.
  - Write a test to verify this retry behavior.

- [ ] **Task 9.4: Commit Changes**
  - Commit with the message: `feat: implement automatic recovery from Claude usage limits`.

---

## **Phase 10: Logging and Final Polish**

**Goal:** Add comprehensive logging and finalize the project.

- [ ] **Task 10.1: Write Test for Logging**
  - In `test_orchestrator.py`, write a test to ensure that after running the orchestrator, a log file is created in the `.claude/logs/` directory.

- [ ] **Task 10.2: Implement Logging**
  - In `automate_dev.py`, add the `setup_logging` function and integrate the `loggers` dictionary throughout the script as detailed in the PRD.
  - Run the test from Task 10.1 to confirm it passes.

- [ ] **Task 10.3: Final Code Review**
  - Review all code files (`automate_dev.py`, `status_mcp_server.py`, tests, and slash commands) for clarity, comments, and adherence to the PRD. Refine as needed.

- [ ] **Task 10.4: Create Project `README.md`**
  - Create a `README.md` in the root directory.
  - Explain the project's purpose, how to set it up (install dependencies, configure MCP server path), and how to run the automation using `python automate_dev.py`.

- [ ] **Task 10.5: Final Commit**
  - Stage all final changes.
  - Commit with the message: `docs: add README and finalize logging and code comments`.

---

## **Progress Summary**

### Completed: 5/10 Phases
- ✅ Phase 0: Project Initialization and Prerequisite Setup
- ✅ Phase 1: Core Orchestrator Scaffolding (TDD)
- ✅ Phase 2: State Management (TaskTracker Class)
- ✅ Phase 3: Claude Command Execution and Signal Handling
- ✅ Phase 4: MCP Server for Reliable Status Reporting

### Notes from Session 2025-01-14
- Implemented 5 complete phases using strict TDD methodology
- Created 22 comprehensive tests with 100% passing rate
- Applied Red-Green-Refactor cycle for each phase
- Enhanced code with type hints, documentation, and error handling
- Applied full TDD cycle with timeout protection and error handling in Phase 3
- Applied full TDD cycle with comprehensive refactoring in Phase 2
- Completed Phase 4 with MCP server implementation and status reporting
- Added 6 new tests for MCP server and get_latest_status functionality