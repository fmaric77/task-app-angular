# Runbook: Header shows only active count, not total

## Symptoms

- Header subtitle shows how many tasks are still active (e.g. "3 tasks remaining")
- User cannot see the total number of tasks (active + completed)
- Count does not reflect the full workload at a glance

## Root cause

`HeaderComponent` only accepts and displays `activeCount`. `TaskService` already tracks all tasks in a signal but exposes no `totalCount` computed, and the app template does not pass total task count to the header.

## Diagnosis

1. Open `src/app/components/header/header.component.html` — subtitle binds only to `activeCount()`
2. Open `src/app/services/task.service.ts` — `activeCount` exists; no `totalCount`
3. Open `src/app/app.component.html` — `<app-header>` passes only `[activeCount]`

## Fix

1. In `src/app/services/task.service.ts`, add:

```typescript
readonly totalCount = computed(() => this.tasks().length);
```

2. In `src/app/components/header/header.component.ts`, add `totalCount = input.required<number>()`.

3. In `src/app/components/header/header.component.html`, show both counts:

```html
{{ activeCount() }} active / {{ totalCount() }} total
```

4. In `src/app/app.component.ts`, expose `totalCount` from the service.

5. In `src/app/app.component.html`, pass `[totalCount]="totalCount()"` to `<app-header>`.

## Verification

```bash
npm run build
```

Manual check:

1. Add several tasks — header shows e.g. "3 active / 3 total"
2. Complete a task — active decreases, total stays the same
3. Delete a task — both counts decrease
4. Reload page — counts persist from localStorage

## Labels

- `header`
- `display`
- `support-agent`
