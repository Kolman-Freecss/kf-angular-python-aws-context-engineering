import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { TaskListComponent } from './components/task-list.component';

@Component({
  selector: 'app-tasks',
  standalone: true,
  imports: [CommonModule, TaskListComponent],
  template: `
    <div class="tasks-container">
      <app-task-list></app-task-list>
    </div>
  `,
  styles: [`
    .tasks-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 1rem;
    }
  `]
})
export class TasksComponent {
}
