import { Component, input, output } from '@angular/core';

@Component({
  selector: 'app-header',
  standalone: true,
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss',
})
export class HeaderComponent {
  activeCount = input.required<number>();
  isDarkMode = input.required<boolean>();
  onToggleTheme = output<void>();
}
