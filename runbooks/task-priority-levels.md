# Runbook / Spec: Task Priority Levels

## Feature summary

Add **priority levels** (High, Medium, Low) to tasks, shown as a colored dot, cyclable by click, with an optional "sort by priority" view. This is a feature implementation, not a bug fix — follow this spec as the source of truth.

## Acceptance criteria

- [ ] Every task has a `priority` of `'high' | 'medium' | 'low'`
- [ ] New tasks default to `'medium'`
- [ ] A colored dot appears to the **left** of the task title:
  - High = red (`#FF3B30`)
  - Medium = orange (`#FF9500`)
  - Low = green (`#34C759`)
- [ ] Clicking the dot cycles priority: Medium → High → Low → Medium
- [ ] A "Sort by priority" toggle in the filter bar sorts High → Medium → Low (when off, keep current newest-first order)
- [ ] Priority persists across page reloads (localStorage)
- [ ] Existing tasks without a stored priority are treated as `'medium'`

## Files to change

### 1. `src/app/models/task.model.ts`
Add `priority` to the `Task` interface (reuse existing `TaskPriority` type):

```typescript
export interface Task {
  id: string;
  title: string;
  completed: boolean;
  createdAt: number;
  priority: TaskPriority;
}
```

### 2. `src/app/services/task.service.ts`
- In `loadFromStorage()`, default any task missing `priority` to `'medium'`.
- In `addTask()`, set `priority: 'medium'` on the new task.
- Add `cyclePriority(id: string)` that maps medium→high→high→low→low→medium and updates the task.
- Add a `sortByPriority` signal (default `false`) and `toggleSortByPriority()`.
- Update `filteredTasks` computed: after filtering, if `sortByPriority()` is true, sort by priority order `{ high: 0, medium: 1, low: 2 }`.

### 3. `src/app/components/task-item/task-item.component.ts`
- Add `onCyclePriority = output<string>()`.
- Add `handleCyclePriority()` that emits `task().id`.

### 4. `src/app/components/task-item/task-item.component.html`
- Add a priority dot button before the checkbox/body:

```html
<button
  type="button"
  class="task-item__priority"
  [class.task-item__priority--high]="task().priority === 'high'"
  [class.task-item__priority--medium]="task().priority === 'medium'"
  [class.task-item__priority--low]="task().priority === 'low'"
  (click)="handleCyclePriority()"
  aria-label="Change priority"
></button>
```

### 5. `src/app/components/task-item/task-item.component.scss`
Add dot styles:

```scss
&__priority {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: none;
  margin-right: 12px;
  padding: 0;
  cursor: pointer;

  &--high { background-color: #ff3b30; }
  &--medium { background-color: #ff9500; }
  &--low { background-color: #34c759; }
}
```

### 6. `src/app/components/task-list/task-list.component.*`
Forward a new `onCyclePriority` output from `TaskItemComponent` up to the parent.

### 7. `src/app/components/filter-bar/filter-bar.component.*`
- Add `sortByPriority = input.required<boolean>()` and `onToggleSort = output<void>()`.
- Add a button "Sort by priority" with active styling when on.

### 8. `src/app/app.component.*`
Wire the service: pass `sortByPriority` to filter bar, handle `onToggleSort` → `toggleSortByPriority()`, handle `onCyclePriority` → `cyclePriority(id)`.

## Verification

```bash
npm run build
```

Manual check:
1. Add a task → orange dot (medium) by default
2. Click the dot → red (high) → green (low) → orange (medium)
3. Add tasks of mixed priorities, toggle "Sort by priority" → high tasks rise to top
4. Reload page → priorities persist

## Labels

- `priority`
- `feature`
- `support-agent`
