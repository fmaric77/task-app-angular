export type FilterType = 'all' | 'active' | 'completed';

export interface Task {
  id: string;
  title: string;
  completed: boolean;
  createdAt: number;
  priority: TaskPriority;
}

export type TaskPriority = 'high' | 'medium' | 'low';

export interface TaskCategory {
  id: string;
  name: string;
  color: string;
}

export interface TaskWithMeta extends Task {
  category?: string;
  notes?: string;
  dueDate?: number;
}
