# Runbook: Task date displays wrong month

## Symptoms

- Task "Added" date shows month off by one (e.g. June task shows `5/24/2026` instead of `6/24/2026`)
- Bug affects every task item in the list
- Title and completion toggle work correctly

## Root cause

`formatDate()` in `src/app/utils/format-date.util.ts` uses `date.getMonth()` directly. JavaScript `getMonth()` is 0-indexed (0 = January, 11 = December), so the displayed month is always one less than the actual month.

## Diagnosis

1. Run the app: `npm start`
2. Add a task today
3. Compare displayed date to actual date — month will be off by one
4. Inspect `src/app/utils/format-date.util.ts`

## Fix

In `src/app/utils/format-date.util.ts`, add 1 to the month:

```typescript
export function formatDate(timestamp: number): string {
  const date = new Date(timestamp);
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const year = date.getFullYear();

  return `${month}/${day}/${year}`;
}
```

Remove the misleading bug comment.

## Verification

```bash
npm run build
```

Manual check:
1. Add a task
2. Confirm "Added" date shows correct month (1–12)

## Labels

- `date`
- `display`
- `support-agent`
