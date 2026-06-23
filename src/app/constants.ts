export const MAX_TASKS = 100;
export const MAX_TASK_TITLE_LENGTH = 200;
export const STORAGE_VERSION = 2;

export const PRIORITY_LEVELS = {
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low',
} as const;

export const TASK_CATEGORIES = [
  'Work',
  'Personal',
  'Shopping',
  'Health',
  'Finance',
] as const;

export const COLORS = {
  primary: '#007AFF',
  success: '#34C759',
  danger: '#FF3B30',
  warning: '#FF9500',
  gray: '#8E8E93',
  lightGray: '#C7C7CC',
  background: '#F2F2F7',
  white: '#FFFFFF',
  black: '#1C1C1E',
};

export const ANIMATION_DURATION = 300;
export const DEBOUNCE_DELAY = 300;

export type PriorityLevel = (typeof PRIORITY_LEVELS)[keyof typeof PRIORITY_LEVELS];
export type TaskCategory = (typeof TASK_CATEGORIES)[number];
