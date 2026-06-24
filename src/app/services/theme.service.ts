import { effect, Injectable, signal } from '@angular/core';

const STORAGE_KEY = '@taskapp_theme';

function loadTheme(): boolean {
  try {
    return localStorage.getItem(STORAGE_KEY) === 'dark';
  } catch {
    return false;
  }
}

function saveTheme(isDark: boolean): void {
  try {
    localStorage.setItem(STORAGE_KEY, isDark ? 'dark' : 'light');
  } catch {
    // silently fail
  }
}

@Injectable({ providedIn: 'root' })
export class ThemeService {
  readonly isDarkMode = signal(loadTheme());

  constructor() {
    effect(() => {
      const isDark = this.isDarkMode();
      document.documentElement.dataset['theme'] = isDark ? 'dark' : 'light';
      saveTheme(isDark);
    });
  }

  toggleDarkMode(): void {
    this.isDarkMode.update(v => !v);
  }
}
