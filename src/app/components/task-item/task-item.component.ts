import { Component, input, output } from '@angular/core';
import { Task } from '../../models/task.model';
import { formatDate } from '../../utils/format-date.util';

@Component({
  selector: 'app-task-item',
  standalone: true,
  templateUrl: './task-item.component.html',
  styleUrl: './task-item.component.scss',
})
export class TaskItemComponent {
  task = input.required<Task>();
  onToggle = output<string>();
  onDelete = output<string>();

  formatDate = formatDate;

  handleDelete(): void {
    this.onDelete.emit(this.task().id);
  }

  handleToggle(): void {
    this.onToggle.emit(this.task().id);
  }
}
