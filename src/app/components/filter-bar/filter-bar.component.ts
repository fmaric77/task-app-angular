import { Component, input, output } from '@angular/core';
import { FilterType } from '../../models/task.model';

const FILTERS: { label: string; value: FilterType }[] = [
  { label: 'All', value: 'all' },
  { label: 'Active', value: 'active' },
  { label: 'Completed', value: 'completed' },
];

@Component({
  selector: 'app-filter-bar',
  standalone: true,
  templateUrl: './filter-bar.component.html',
  styleUrl: './filter-bar.component.scss',
})
export class FilterBarComponent {
  readonly filters = FILTERS;

  activeFilter = input.required<FilterType>();
  completedCount = input.required<number>();
  sortByPriority = input.required<boolean>();
  onFilterChange = output<FilterType>();
  onClearCompleted = output<void>();
  onToggleSort = output<void>();

  handleClear(): void {
    this.onClearCompleted.emit();
  }

  handleToggleSort(): void {
    this.onToggleSort.emit();
  }
}
