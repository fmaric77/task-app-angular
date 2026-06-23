---
name: Code Review
description: Review code for quality issues, anti-patterns, and convention violations. Automatically activates when the user asks for a review, or when reviewing test files, PRs, or pre-commit changes.
version: 1.0.0
---

# Code Review

Perform thorough code reviews checking for quality issues, anti-patterns, convention violations, and potential bugs.

## When to Activate

- The user asks to review a file, PR, or set of changes
- The user asks to check code quality before committing
- The user mentions "pre-commit review" or "code review"
- The user asks to review test code specifically

## General Code Review

Check for:

### Correctness
- Logic errors, off-by-one bugs, null/undefined risks
- Missing error handling at system boundaries
- Race conditions or stale state in async code
- Incorrect types or type assertions that hide issues

### Conventions
- Read the project rules (`.cursorrules`, `.cursor/rules/`) and check compliance
- Flag deviations with the specific rule being violated
- Check naming, exports, import ordering, styling approach

### Dead Code
- Unused imports, variables, functions, types
- Commented-out code blocks
- Unreachable branches

### Performance
- Unnecessary re-renders (missing memoization on expensive computations)
- Large objects in dependency arrays
- Missing cleanup in effects

## Test Code Review

When reviewing test files, additionally check for:

### Reliability
- **Hardcoded waits** — `setTimeout`, `sleep`, arbitrary delays. Should use proper async utilities (`waitFor`, `findBy*`)
- **Brittle selectors** — querying by component tree structure, child indices, CSS classes. Should use `testID`, `getByText`, `getByRole`
- **Flaky patterns** — tests that depend on timing, network, or execution order

### Assertions
- **Weak assertions** — `.toBeTruthy()`, `.toBeDefined()` when specific value checks are possible
- **Missing assertions** — `jest.fn()` created but never verified with `.toHaveBeenCalled()`
- **Wrong level** — asserting implementation details instead of behavior

### Isolation
- **Shared mutable state** — variables modified across tests without reset
- **Order dependence** — tests that fail when run individually
- **Missing cleanup** — side effects that leak between tests

### Coverage Gaps
- Missing edge cases (empty input, max length, special characters)
- Missing error scenarios
- Missing accessibility checks
- Commented-out or skipped tests with no tracking issue

## Output Format

For each finding:

```
**[SEVERITY] Issue Title**
File: `path/to/file.ts:LINE`
What: [Description of the issue]
Why it matters: [Impact — bug risk, flakiness, maintenance burden]
Fix: [Specific suggestion]
```

Severity levels:
- **CRITICAL** — Will cause bugs or test failures
- **WARNING** — Anti-pattern, reliability risk, or convention violation
- **INFO** — Suggestion for improvement, not blocking

## After Review

If the user asks to fix the issues:
1. Fix in priority order (critical first)
2. Show the diff for each fix
3. Re-run tests if applicable to verify fixes don't break anything
