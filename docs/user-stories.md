# User Stories for Demo

Use these for Demo 4 (Test Case Generation from Requirements).

---

## User Story 1: Task Priority Levels

**As a** user
**I want to** set priority levels (High, Medium, Low) on my tasks
**So that** I can focus on what matters most

### Acceptance Criteria
- [ ] Each task can be assigned a priority: High, Medium, or Low
- [ ] Default priority for new tasks is "Medium"
- [ ] Priority is displayed as a colored indicator on the task item (Red = High, Orange = Medium, Green = Low)
- [ ] User can change priority by tapping the priority indicator
- [ ] Tasks can be sorted by priority (High first)
- [ ] Priority persists across app restarts
- [ ] Filter bar includes a "By Priority" sort option

### Design Notes
- Priority indicator is a small colored dot to the left of the task title
- Tapping the dot cycles through: Medium → High → Low → Medium
- Sort by priority is secondary sort (within each priority, maintain creation order)

---

## User Story 2: Swipe to Delete with Undo

**As a** user
**I want to** swipe left on a task to delete it, with an undo option
**So that** I don't accidentally lose tasks

### Acceptance Criteria
- [ ] Swiping left on a task row reveals a red "Delete" action
- [ ] Swiping past 50% of the row width auto-triggers delete
- [ ] After deletion, a toast/snackbar appears at the bottom: "Task deleted" with an "Undo" button
- [ ] Undo restores the task to its original position and state
- [ ] Toast auto-dismisses after 5 seconds
- [ ] If another task is deleted while a toast is showing, the previous deletion is finalized and a new toast appears
- [ ] The existing delete button (X) on each task still works but also shows the undo toast
- [ ] Undo is not available after app restart

### Edge Cases
- Deleting the last task in a filtered view should show the empty state
- Rapid sequential deletes should queue properly
- Undo after toggling a filter should still work
