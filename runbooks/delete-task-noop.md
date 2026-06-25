# Runbook: Delete task button does nothing

## Symptoms

- User clicks the delete button on a task
- Task remains in the list
- Task count does not decrease
- Delete button is visible and clickable but has no effect

## Root cause

`TaskService.deleteTask()` in `src/app/services/task.service.ts` is a stub — the method body is empty with a TODO comment. The task item component correctly emits the delete event and `AppComponent` delegates to the service, but the service never removes the task.

## Diagnosis

1. Run the app: `npm start`
2. Add a task
3. Click the delete button on the task
4. Task still appears in the list
5. Inspect `src/app/services/task.service.ts` — find empty `deleteTask()` method

## Fix

In `src/app/services/task.service.ts`, implement `deleteTask()`:

```typescript
deleteTask(id: string): void {
  this.tasks.update(tasks => tasks.filter(t => t.id !== id));
}
```

Remove the TODO comment.

## Verification

```bash
npm run build
```

Manual check:
1. Add two tasks
2. Delete one task
3. Only the remaining task appears in the list
4. Refresh page — persistence should reflect the deletion

## Labels

- `delete`
- `support-agent`
