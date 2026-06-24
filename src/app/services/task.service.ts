import { computed, effect, Injectable, signal } from '@angular/core';
import { FilterType, Task, TaskPriority } from '../models/task.model';

const STORAGE_KEY = '@taskapp_tasks';

const PRIORITY_ORDER: Record<TaskPriority, number> = {
  high: 0,
  medium: 1,
  low: 2,
};

function loadFromStorage(): Task[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const tasks: Task[] = raw ? JSON.parse(raw) : [];
    return tasks.map(t => ({
      ...t,
      priority: t.priority ?? 'medium',
    }));
  } catch {
    return [];
  }
}

function saveToStorage(tasks: Task[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
  } catch {
    // silently fail -- UI state remains correct even if persist fails
  }
}

@Injectable({ providedIn: 'root' })
export class TaskService {
  readonly tasks = signal<Task[]>([]);
  readonly filter = signal<FilterType>('all');
  readonly sortByPriority = signal(false);
  readonly isLoading = signal(true);

  readonly filteredTasks = computed(() => {
    const currentFilter = this.filter();
    const allTasks = this.tasks();
    const sortByPriority = this.sortByPriority();

    const filtered = allTasks.filter(t => {
      if (currentFilter === 'active') {
        return !t.completed;
      }
      if (currentFilter === 'completed') {
        return t.completed;
      }
      return true;
    });

    if (sortByPriority) {
      return [...filtered].sort(
        (a, b) => PRIORITY_ORDER[a.priority] - PRIORITY_ORDER[b.priority],
      );
    }

    return filtered;
  });

  readonly activeCount = computed(() =>
    this.tasks().filter(t => !t.completed).length,
  );

  readonly completedCount = computed(() =>
    this.tasks().filter(t => t.completed).length,
  );

  constructor() {
    this.tasks.set(loadFromStorage());
    this.isLoading.set(false);

    effect(() => {
      saveToStorage(this.tasks());
    });
  }

  setFilter(filter: FilterType): void {
    this.filter.set(filter);
  }

  toggleSortByPriority(): void {
    this.sortByPriority.update(v => !v);
  }

  addTask(title: string): void {
    const trimmed = title.trim();
    if (!trimmed) {
      return;
    }

    const newTask: Task = {
      id: Date.now().toString(),
      title: trimmed,
      completed: false,
      createdAt: Date.now(),
      priority: 'medium',
    };

    this.tasks.update(tasks => [newTask, ...tasks]);
  }

  toggleTask(id: string): void {
    this.tasks.update(tasks =>
      tasks.map(t => (t.id === id ? { ...t, completed: !t.completed } : t)),
    );
  }

  deleteTask(id: string): void {
    this.tasks.update(tasks => tasks.filter(t => t.id !== id));
  }

  clearCompleted(): void {
    this.tasks.update(tasks => tasks.filter(t => !t.completed));
  }

  cyclePriority(id: string): void {
    const next: Record<TaskPriority, TaskPriority> = {
      medium: 'high',
      high: 'low',
      low: 'medium',
    };

    this.tasks.update(tasks =>
      tasks.map(t =>
        t.id === id ? { ...t, priority: next[t.priority] } : t,
      ),
    );
  }
}
