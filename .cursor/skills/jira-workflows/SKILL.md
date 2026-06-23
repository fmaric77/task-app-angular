---
name: Jira Workflows
description: Pull, reference, and update Jira tickets using the Atlassian MCP. Automatically activates when work involves Jira tickets, feature implementation from requirements, or status updates.
version: 1.0.0
---

# Jira Workflows

You have access to Jira via the Atlassian MCP server. Use it to pull ticket context, reference requirements, and update ticket status as work progresses.

## When to Activate

- The user mentions a Jira ticket key (e.g., SCRUM-6, PROJ-123)
- The user asks to implement a feature, fix a bug, or work on a task that likely has a Jira ticket
- The user asks to update progress or status on work
- The user asks for requirements, acceptance criteria, or specs for a feature

## Pulling a Ticket

When you need context from a Jira ticket:

1. Use the Atlassian MCP to fetch the issue by key
2. Extract and summarize:
   - **Summary** and **description**
   - **Acceptance criteria** (look for these in the description, often under "## Acceptance Criteria" or as a checklist)
   - **Issue type** (Story, Bug, Task) — this affects how you approach the work
   - **Status** and **priority**
   - **Parent epic** if present — gives broader context
   - **Edge cases** or technical notes if included
3. Present a concise summary before starting work, confirming what you'll implement

## Implementing from a Ticket

When implementing a feature or fix from a Jira ticket:

1. Pull the ticket first (as above)
2. Confirm the approach with the user before writing code
3. Address ALL acceptance criteria — check them off mentally as you go
4. Reference the ticket key in any commit messages or PR descriptions
5. Flag if any AC is ambiguous or seems incomplete

## Updating a Ticket

When the user asks to update a ticket:

1. Use the Atlassian MCP to add a comment with the update
2. Transition the ticket status if appropriate:
   - Starting work → "In Progress"
   - Ready for review → "In Review"
   - Completed → "Done"
3. Keep comments concise and technical — what was done, any decisions made, any blockers

## Searching for Tickets

When the user needs to find tickets:

- Use JQL queries via the Atlassian MCP
- Common queries:
  - `project = SCRUM AND status != Done ORDER BY priority DESC` — active backlog
  - `project = SCRUM AND type = Bug AND status != Done` — open bugs
  - `project = SCRUM AND sprint in openSprints()` — current sprint

## Important

- Always pull the latest ticket data before implementing — don't rely on stale context
- If a ticket's AC conflicts with the existing codebase patterns, flag it
- Never update ticket status without the user's confirmation
