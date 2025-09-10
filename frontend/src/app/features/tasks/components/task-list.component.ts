import { CommonModule } from '@angular/common';
import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { Category, Task, TaskService } from '../../../core/services/task.service';
import { TaskCardComponent } from './task-card.component';
import { TaskFiltersComponent } from './task-filters.component';
import { TaskFormComponent } from './task-form.component';

@Component({
  selector: 'app-task-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    TaskCardComponent,
    TaskFormComponent,
    TaskFiltersComponent
  ],
  template: `
    <div class="task-list-container">
      <div class="task-list-header">
        <h2>My Tasks</h2>
        <button 
          class="btn-primary" 
          (click)="showCreateForm.set(!showCreateForm())"
          data-testid="add-task-btn">
          {{ showCreateForm() ? 'Cancel' : 'Add New Task' }}
        </button>
      </div>

      <!-- Task Creation Form -->
      <div *ngIf="showCreateForm()" class="task-form-container">
        <app-task-form 
          [categories]="categories()"
          (taskCreated)="onTaskCreated($event)"
          (cancel)="showCreateForm.set(false)">
        </app-task-form>
      </div>

      <!-- Filters -->
      <app-task-filters
        [categories]="categories()"
        (filtersChanged)="onFiltersChanged($event)">
      </app-task-filters>

      <!-- Loading State -->
      <div *ngIf="loading()" class="loading-state">
        <div class="spinner"></div>
        <p>Loading tasks...</p>
      </div>

      <!-- Error State -->
      <div *ngIf="error()" class="error-state">
        <p>{{ error() }}</p>
        <button class="btn-secondary" (click)="loadTasks()">Retry</button>
      </div>

      <!-- Tasks Grid -->
      <div *ngIf="!loading() && !error()" class="tasks-grid">
        <div *ngIf="tasks().length === 0" class="empty-state">
          <h3>No tasks found</h3>
          <p>Create your first task to get started!</p>
        </div>
        
        <app-task-card
          *ngFor="let task of tasks(); trackBy: trackByTaskId"
          [task]="task"
          [categories]="categories()"
          (taskUpdated)="onTaskUpdated($event)"
          (taskDeleted)="onTaskDeleted($event)">
        </app-task-card>
      </div>

      <!-- Pagination -->
      <div *ngIf="!loading() && !error() && totalTasks() > 0" class="pagination">
        <button 
          class="btn-secondary" 
          [disabled]="currentPage() <= 1"
          (click)="goToPage(currentPage() - 1)"
          data-testid="prev-page-btn">
          Previous
        </button>
        
        <span class="page-info">
          Page {{ currentPage() }} of {{ totalPages() }}
          ({{ totalTasks() }} total tasks)
        </span>
        
        <button 
          class="btn-secondary" 
          [disabled]="currentPage() >= totalPages()"
          (click)="goToPage(currentPage() + 1)"
          data-testid="next-page-btn">
          Next
        </button>
      </div>
    </div>
  `,
  styles: [`
    .task-list-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 1rem;
    }

    .task-list-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
    }

    .task-list-header h2 {
      margin: 0;
      color: #2c3e50;
    }

    .btn-primary {
      background-color: #3498db;
      color: white;
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 4px;
      cursor: pointer;
      font-size: 1rem;
      transition: background-color 0.3s;
    }

    .btn-primary:hover {
      background-color: #2980b9;
    }

    .btn-secondary {
      background-color: #95a5a6;
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.9rem;
      transition: background-color 0.3s;
    }

    .btn-secondary:hover:not(:disabled) {
      background-color: #7f8c8d;
    }

    .btn-secondary:disabled {
      background-color: #bdc3c7;
      cursor: not-allowed;
    }

    .task-form-container {
      margin-bottom: 2rem;
      padding: 1rem;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .loading-state, .error-state, .empty-state {
      text-align: center;
      padding: 3rem;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .spinner {
      width: 40px;
      height: 40px;
      border: 4px solid #f3f3f3;
      border-top: 4px solid #3498db;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 1rem;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .error-state p {
      color: #e74c3c;
      margin-bottom: 1rem;
    }

    .empty-state h3 {
      color: #2c3e50;
      margin-bottom: 0.5rem;
    }

    .empty-state p {
      color: #7f8c8d;
    }

    .tasks-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1rem;
      margin-bottom: 2rem;
    }

    .pagination {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 1rem;
      padding: 1rem;
    }

    .page-info {
      font-size: 0.9rem;
      color: #7f8c8d;
    }

    @media (max-width: 768px) {
      .task-list-header {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
      }

      .tasks-grid {
        grid-template-columns: 1fr;
      }

      .pagination {
        flex-direction: column;
        gap: 0.5rem;
      }
    }
  `]
})
export class TaskListComponent implements OnInit {
  private taskService = inject(TaskService);

  // Signals for reactive state management
  tasks = signal<Task[]>([]);
  categories = signal<Category[]>([]);
  loading = signal(false);
  error = signal<string | null>(null);
  showCreateForm = signal(false);
  currentPage = signal(1);
  totalTasks = signal(0);
  pageSize = signal(10);
  currentFilters = signal<any>({});

  // Computed values
  totalPages = computed(() => Math.ceil(this.totalTasks() / this.pageSize()));

  ngOnInit(): void {
    this.loadCategories();
    this.loadTasks();
  }

  loadTasks(): void {
    this.loading.set(true);
    this.error.set(null);

    const filters = this.currentFilters();
    this.taskService.getTasks(this.currentPage(), this.pageSize(), filters).subscribe({
      next: (response) => {
        this.tasks.set(response.tasks);
        this.totalTasks.set(response.total);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Failed to load tasks. Please try again.');
        this.loading.set(false);
        console.error('Error loading tasks:', err);
      }
    });
  }

  loadCategories(): void {
    this.taskService.getCategories().subscribe({
      next: (categories) => {
        this.categories.set(categories);
      },
      error: (err) => {
        console.error('Error loading categories:', err);
      }
    });
  }

  onTaskCreated(task: Task): void {
    this.showCreateForm.set(false);
    this.loadTasks(); // Refresh the list
  }

  onTaskUpdated(task: Task): void {
    // Update the task in the list
    const currentTasks = this.tasks();
    const index = currentTasks.findIndex(t => t.id === task.id);
    if (index !== -1) {
      const updatedTasks = [...currentTasks];
      updatedTasks[index] = task;
      this.tasks.set(updatedTasks);
    }
  }

  onTaskDeleted(taskId: number): void {
    // Remove the task from the list
    const currentTasks = this.tasks();
    const filteredTasks = currentTasks.filter(t => t.id !== taskId);
    this.tasks.set(filteredTasks);
    this.totalTasks.set(this.totalTasks() - 1);
  }

  onFiltersChanged(filters: any): void {
    this.currentFilters.set(filters);
    this.currentPage.set(1); // Reset to first page
    this.loadTasks();
  }

  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages()) {
      this.currentPage.set(page);
      this.loadTasks();
    }
  }

  trackByTaskId(index: number, task: Task): number {
    return task.id;
  }
}
