import { computed, effect, Injectable, signal } from '@angular/core';
import { FilterType, Task } from '../models/task.model';

const STORAGE_KEY = '@taskapp_tasks';

function loadFromStorage(): Task[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
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
  readonly isLoading = signal(true);

  readonly filteredTasks = computed(() => {
    const currentFilter = this.filter();
    const allTasks = this.tasks();

    return allTasks.filter(t => {
      if (currentFilter === 'active') {
        return !t.completed;
      }
      if (currentFilter === 'completed') {
        return t.completed;
      }
      return true;
    });
  });

  readonly activeCount = computed(() =>
    this.tasks().filter(t => !t.completed).length,
  );

  readonly totalCount = computed(() => this.tasks().length);

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

  // TODO: Implement clearCompleted - remove all tasks where completed === true
  clearCompleted(): void {}
}
