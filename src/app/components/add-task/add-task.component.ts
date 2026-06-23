import { Component, output } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-add-task',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './add-task.component.html',
  styleUrl: './add-task.component.scss',
})
export class AddTaskComponent {
  value = '';
  onAdd = output<string>();

  handleAdd(): void {
    if (!this.value.trim()) {
      return;
    }
    this.onAdd.emit(this.value);
    this.value = '';
  }
}
