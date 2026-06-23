---
name: Test Case Generation
description: Generate structured, comprehensive test cases from requirements, user stories, or Jira tickets. Automatically activates when the user asks for test cases, test coverage, or QA artifacts.
version: 1.0.0
---

# Test Case Generation

Generate structured test cases from feature descriptions, user stories, acceptance criteria, or Jira tickets.

## When to Activate

- The user asks for test cases, test scenarios, or test coverage for a feature
- The user asks to create QA artifacts from a user story or Jira ticket
- The user mentions generating tests from requirements or acceptance criteria

## Process

### 1. Gather Requirements

Get the source material. In order of preference:
- **Jira ticket** — use the Jira Workflows skill to pull the ticket and extract AC
- **User story** — look for it in `docs/`, project files, or the user's message
- **Feature description** — work from whatever the user provides

### 2. Generate Test Cases

Organize into three categories:

**Positive / Happy Path**
- The core flows that should work as described in the AC
- One test case per acceptance criterion at minimum

**Negative Cases**
- Invalid inputs, missing required fields, unauthorized actions
- What happens when the user does something wrong

**Edge Cases**
- Boundary values (min, max, zero, empty, one-off)
- Concurrent actions, race conditions, interruptions
- State transitions (what if the user is mid-action and something changes)

### 3. Output Location

Save generated test case files to `docs/` using the naming convention `<TICKET-KEY>-test-cases.md` (e.g., `docs/SCRUM-6-test-cases.md`). Never place test case documents in `__tests__/` — that directory is reserved for executable test code.

### 4. Output Format

Use this structure for each test case:

```
### TC-XXX: [Title]

**Priority:** P1 / P2 / P3 / P4
**Category:** Happy Path / Negative / Edge Case
**Preconditions:** [What must be true before the test starts]

**Steps:**
1. [Action]
2. [Action]
3. [Action]

**Expected Result:**
- [What should happen]
- [What should be visible/verifiable]
```

### 5. Coverage Check

After generating, review against the source requirements:
- Every acceptance criterion has at least one test case
- Boundary values are covered for any inputs with constraints
- Error states and empty states are covered
- Persistence scenarios if data is stored (survives restart, handles corruption)

## Priority Definitions

| Priority | Meaning | Example |
|----------|---------|---------|
| P1 | Core functionality, blocks release | Happy path fails |
| P2 | Important but has workaround | Edge case in secondary flow |
| P3 | Minor impact, cosmetic or UX | Formatting inconsistency |
| P4 | Trivial, nice to verify | Tooltip text accuracy |

## Tips

- If working from a Jira ticket, check for linked tickets or parent epic — they may add context
- Always include at least one "rapid interaction" test (fast taps, double submissions)
- For mobile: consider device-specific scenarios (rotation, background/foreground, low memory)
- Call out any gaps in the requirements — "AC doesn't specify behavior for [X], assumed [Y]"
