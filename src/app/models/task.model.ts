export type FilterType = 'all' | 'active' | 'completed';

export interface Task {
  id: string;
  title: string;
  completed: boolean;
  createdAt: number;
}

export type TaskPriority = 'high' | 'medium' | 'low';

export interface TaskCategory {
  id: string;
  name: string;
  color: string;
}

export interface TaskWithMeta extends Task {
  priority?: TaskPriority;
  category?: string;
  notes?: string;
  dueDate?: number;
}
