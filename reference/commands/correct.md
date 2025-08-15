The TDD validation has failed OR a git push operation failed. Review and correct the issues that prevented the loop from continuing.

Identify all of the failures from our recent validation. Look at the situation through the eyes of a senior developer. What is the best course of action for these types of failures? Our goal is to have all issues properly solved before we continue with our project. That means that all tests should be passing. No tests should be inappropriately skipped. We should not have substantial implementation without test coverage. If tests were inappropriately modified as a shortcut to make implementation pass, then we should reevaluate and correct. Tests should only be modified if we determine with high confidence that a test is indeed incorrect. The integrity of our project and our TDD workflow relies on our tests being written properly. They are used as the truth that we implement against. If you are unsure of whether a test was written incorrectly, use tools such as context7 and web search to research the issues. Continue until you have high confidence in your understanding of how to properly write each test.

Before you change a test, ask yourself these questions:

1. Have I thoroughly researched what this test is testing and determined that it's truly incorrect?
2. Do I have high confidence in the knowledge that I'm using to make this decision?
3. If I change this test, would it be considered a workaround or shortcut?
4. Have I factored in how changing this test will affect the rest of the project?

If you answered no to #1, #2, or #4, and/or yes to #3 then you should think harder and do more research before changing the test. It's possible that this test should not be changed. And you should make sure that you have a full understanding of the impact before continuing. ONLY change a test if you determine with high confidence that the tests is indeed wrong.

TOOLS AVAILABLE:

- Web Search (search the web for answers)
- Context7 (search for coding guidelines and samples)
- LEANN (semantic search of current project structure and project documentation)

Ask yourself these questions:

1. Do we still have technical debt if we continue development from the current state?
2. Have any shortcuts been taken that do not align with best practices?
3. Did I skip something because it looked too complex?
4. Did I simplify something as a shortcut?
5. Do I have lint or typescript errors?

If the answer to any of these questions is yes, then we need to go back and perform any necessary corrections properly until we can confidently and truthfully answer no to all of these questions. And this even applies if there are issues that are left over from previous sessions and previous work. We want to move forward with a completely clean project. Let's say this explicitly: We want ALL problems to be solved. Not just issues related to the work from this session.