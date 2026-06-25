I just joined this project and have never seen this codebase before. Give me a full onboarding briefing.

## What I Need

### 1. Project Overview
- What does this app do? Who is it for?
- Tech stack and key dependencies
- How to run it locally

### 2. Architecture & Structure
- Project folder structure and what lives where
- Key components and how they connect (data flow)
- State management approach
- Navigation structure (if any)
- Any external services, APIs, or storage mechanisms

### 3. Patterns & Conventions
- Coding style and conventions in use (component patterns, naming, exports)
- Read the project rules (`.cursorrules`, `.cursor/rules/`) and summarize what the team expects
- Note anywhere the actual code **deviates** from the stated rules — flag inconsistencies

### 4. Codebase Health Check
Scan the entire codebase and flag anything that needs attention:
- **Code smells:** inconsistent styles, mixed patterns, poor naming
- **Dead code:** unused imports, unreachable functions, files nothing references, commented-out blocks, unused exports
- **Bugs:** anything that looks incorrect (off-by-one errors, missing implementations, TODOs)
- **Test coverage:** assess existing test quality and gaps
- **For each finding:** explain what you found, where it is, and why it matters

### 5. Recommended First Actions
Based on your findings, suggest a prioritized list of what I should tackle first to get this codebase into good shape.

## Output Format
Structure your response with clear headings for each section. Be specific — reference actual file names, function names, and line numbers. Don't be generic.
