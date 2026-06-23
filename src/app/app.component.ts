import { Component, inject } from '@angular/core';
import { AddTaskComponent } from './components/add-task/add-task.component';
import { FilterBarComponent } from './components/filter-bar/filter-bar.component';
import { HeaderComponent } from './components/header/header.component';
import { TaskListComponent } from './components/task-list/task-list.component';
import { TaskService } from './services/task.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    HeaderComponent,
    AddTaskComponent,
    FilterBarComponent,
    TaskListComponent,
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  private readonly taskService = inject(TaskService);

  readonly isLoading = this.taskService.isLoading;
  readonly activeCount = this.taskService.activeCount;
  readonly completedCount = this.taskService.completedCount;
  readonly filter = this.taskService.filter;
  readonly tasks = this.taskService.filteredTasks;

  addTask(title: string): void {
    this.taskService.addTask(title);
  }

  setFilter(filter: 'all' | 'active' | 'completed'): void {
    this.taskService.setFilter(filter);
  }

  toggleTask(id: string): void {
    this.taskService.toggleTask(id);
  }

  deleteTask(id: string): void {
    this.taskService.deleteTask(id);
  }

  clearCompleted(): void {
    this.taskService.clearCompleted();
  }
}
