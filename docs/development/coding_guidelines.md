# Coding Guidelines for AI Assistants

## Core Principles

As an AI assistant helping with code, you should:

- familiarize yourself with the code base by running tree
- we are always using ruff and uv for venv management and linting
- After making changes, always remind the developer to restart services for testing
- Look for existing code to iterate on instead of creating new code
- Do not drastically change established patterns before trying to improve existing ones
- Remind developers to stop existing related services before starting new ones
- Always prefer simple solutions over complex ones

## Code Quality Requirements

When generating or modifying code:

- Avoid duplication by checking for other areas of the codebase with similar functionality
- Consider different environments (dev, test, prod) in your implementation
- Only make changes that are specifically requested or clearly related to the task
- When fixing issues, exhaust all options within the existing implementation before suggesting new patterns or technologies
- If introducing a new pattern, suggest removing the old implementation to avoid duplicate logic
- Keep the codebase clean and organized
- Avoid writing one-off scripts in application files
- Recommend refactoring when files exceed 200-300 lines of code
- Never suggest mocking data for dev or prod environments (only for tests)
- Never suggest adding stubbing or fake data patterns that affect dev or prod environments
- Never suggest overwriting .env files without explicit confirmation
- Focus strictly on code relevant to the task at hand
- Do not modify unrelated code
- Suggest thorough tests for all major functionality
- Avoid suggesting major architectural changes to well-functioning features unless explicitly requested
- Consider potential side effects in other methods and code areas that might be affected by changes

## Implementation Approach

When implementing solutions:

1. Analyze the existing codebase structure first
2. Identify reusable patterns and components
3. Suggest improvements that maintain consistency with existing code
4. Provide complete, working implementations
5. Include appropriate error handling
6. Add comments for complex logic
7. Consider performance implications
8. Suggest test cases that cover the implementation

## Communication

When explaining your code suggestions:

- Clearly explain the rationale behind implementation choices
- Highlight potential issues or edge cases
- Provide context about how the solution fits within the existing architecture
- Ask clarifying questions when requirements are ambiguous
- Present alternatives when relevant, with pros and cons
- Be specific about what files need to be modified and how

---

These guidelines help ensure high-quality, maintainable code that integrates well with existing codebases while minimizing potential issues. They emphasize working within established patterns and focusing on simplicity and quality.