# Runbook: Clear completed button does nothing

## Symptoms

- User clicks **Clear completed** in the filter bar
- Completed tasks remain in the list
- Completed count does not decrease
- Button is visible when `completedCount > 0` but has no effect

## Root cause

`TaskService.clearCompleted()` in `src/app/services/task.service.ts` is a stub — the method body is empty with a TODO comment. The filter bar correctly emits the event and `AppComponent` delegates to the service, but the service never removes completed tasks.

## Diagnosis

1. Run the app: `npm start`
2. Add a task, mark it complete
3. Click **Clear completed**
4. Task still appears under **All** and **Completed** filters
5. Inspect `src/app/services/task.service.ts` — find empty `clearCompleted()` method

## Fix

In `src/app/services/task.service.ts`, implement `clearCompleted()`:

```typescript
clearCompleted(): void {
  this.tasks.update(tasks => tasks.filter(t => !t.completed));
}
```

Remove the TODO comment.

## Verification

```bash
npm run build
```

Manual check:
1. Add two tasks, complete one
2. Click **Clear completed**
3. Only the active task remains
4. **Completed** filter shows empty state
5. Refresh page — persistence should keep only active tasks

## Labels

- `clear-completed`
- `filter`
- `support-agent`
