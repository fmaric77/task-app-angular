{{input}}

Create comprehensive, well-structured documentation based on the input above.

## If No Input Was Provided

Ask the user what they'd like documented. Offer these common options:
- A specific file, function, or component
- An entire module or feature area
- API surface / public interfaces
- Architecture and data flow
- Setup and getting-started guide
- The full project

Then wait for a response before proceeding.

## Documentation Process

### 1. Understand the Scope
- Identify every file, component, function, type, and hook relevant to the subject
- Trace data flow and dependencies — what calls what, what imports what
- Note any external integrations, APIs, or storage mechanisms involved

### 2. Write the Documentation

Structure the output with clear markdown headings. Include all of the following that are relevant:

**Overview** — What it does, why it exists, and where it fits in the broader system.

**Usage** — How to use it. Include code examples pulled from the actual codebase (reference real file names and line numbers). If it's a component, show its props/API. If it's a hook, show the return value and typical call site.

**Architecture & Data Flow** — How the pieces connect. Describe the flow from entry point through any state management, side effects, and rendering. Use a bullet-point or numbered flow when helpful.

**Key Implementation Details** — Non-obvious behavior, edge cases, error handling, performance considerations, or design decisions worth knowing about.

**Types & Interfaces** — Document all relevant TypeScript types, interfaces, and enums with descriptions of each field.

**Dependencies** — What it depends on (internal modules, external packages) and what depends on it.

**Configuration** — Any environment variables, constants, or config values that affect behavior.

**Testing** — Existing test coverage, how to run relevant tests, and any gaps worth noting.

**Known Limitations & TODOs** — Anything incomplete, fragile, or explicitly marked as a TODO in the code.

### 3. Quality Standards
- Be specific: reference actual file paths, function names, and line numbers
- Include real code snippets — don't paraphrase when showing the actual code is clearer
- Don't document the obvious — skip trivial getters/setters and self-explanatory one-liners
- Call out anything surprising, inconsistent, or undocumented that a developer would want to know
- Write for a developer who is seeing this code for the first time

## Output Format
Write the documentation directly in your response with clear markdown headings. Keep it scannable — use tables for props/types when there are more than a few fields, bullet lists for flows, and code blocks for examples.
