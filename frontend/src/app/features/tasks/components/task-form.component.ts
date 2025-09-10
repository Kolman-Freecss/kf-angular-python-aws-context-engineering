import { CommonModule } from '@angular/common';
import { Component, EventEmitter, inject, Input, Output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Category, Task, TaskCreate, TaskService } from '../../../core/services/task.service';

@Component({
  selector: 'app-task-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <form class="task-form" (ngSubmit)="onSubmit()" #taskForm="ngForm">
      <div class="form-header">
        <h3>Create New Task</h3>
      </div>

      <div class="form-group">
        <label for="title" class="required">Title</label>
        <input
          id="title"
          type="text"
          [(ngModel)]="formData.title"
          name="title"
          required
          maxlength="255"
          data-testid="task-title-input"
          #titleInput="ngModel">
        <div *ngIf="titleInput.invalid && titleInput.touched" class="error-message">
          Title is required and must be less than 255 characters.
        </div>
      </div>

      <div class="form-group">
        <label for="description">Description</label>
        <textarea
          id="description"
          [(ngModel)]="formData.description"
          name="description"
          rows="4"
          data-testid="task-description-input">
        </textarea>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="status">Status</label>
          <select
            id="status"
            [(ngModel)]="formData.status"
            name="status"
            data-testid="task-status-select">
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
          </select>
        </div>

        <div class="form-group">
          <label for="priority">Priority</label>
          <select
            id="priority"
            [(ngModel)]="formData.priority"
            name="priority"
            data-testid="task-priority-select">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="category">Category</label>
          <select
            id="category"
            [(ngModel)]="formData.category_id"
            name="category"
            data-testid="task-category-select">
            <option value="">No Category</option>
            <option 
              *ngFor="let category of categories" 
              [value]="category.id">
              {{ category.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="due-date">Due Date</label>
          <input
            id="due-date"
            type="datetime-local"
            [(ngModel)]="formData.due_date"
            name="dueDate"
            data-testid="task-due-date-input">
        </div>
      </div>

      <div class="form-actions">
        <button
          type="submit"
          class="btn-primary"
          [disabled]="taskForm.invalid || submitting()"
          data-testid="create-task-btn">
          {{ submitting() ? 'Creating...' : 'Create Task' }}
        </button>
        
        <button
          type="button"
          class="btn-secondary"
          (click)="onCancel()"
          [disabled]="submitting()"
          data-testid="cancel-create-btn">
          Cancel
        </button>
      </div>

      <div *ngIf="error()" class="error-message">
        {{ error() }}
      </div>
    </form>
  `,
  styles: [`
    .task-form {
      background: white;
      padding: 1.5rem;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .form-header {
      margin-bottom: 1.5rem;
    }

    .form-header h3 {
      margin: 0;
      color: #2c3e50;
      font-size: 1.2rem;
    }

    .form-group {
      margin-bottom: 1rem;
    }

    .form-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
    }

    .form-group label {
      display: block;
      margin-bottom: 0.5rem;
      font-weight: 500;
      color: #2c3e50;
      font-size: 0.9rem;
    }

    .form-group label.required::after {
      content: ' *';
      color: #e74c3c;
    }

    .form-group input,
    .form-group textarea,
    .form-group select {
      width: 100%;
      padding: 0.75rem;
      border: 1px solid #bdc3c7;
      border-radius: 4px;
      font-size: 0.9rem;
      transition: border-color 0.3s;
    }

    .form-group input:focus,
    .form-group textarea:focus,
    .form-group select:focus {
      outline: none;
      border-color: #3498db;
      box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
    }

    .form-group textarea {
      resize: vertical;
      min-height: 80px;
    }

    .form-actions {
      display: flex;
      gap: 1rem;
      justify-content: flex-end;
      margin-top: 1.5rem;
      padding-top: 1rem;
      border-top: 1px solid #ecf0f1;
    }

    .btn-primary {
      background-color: #3498db;
      color: white;
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.9rem;
      font-weight: 500;
      transition: background-color 0.3s;
    }

    .btn-primary:hover:not(:disabled) {
      background-color: #2980b9;
    }

    .btn-primary:disabled {
      background-color: #bdc3c7;
      cursor: not-allowed;
    }

    .btn-secondary {
      background-color: #95a5a6;
      color: white;
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.9rem;
      font-weight: 500;
      transition: background-color 0.3s;
    }

    .btn-secondary:hover:not(:disabled) {
      background-color: #7f8c8d;
    }

    .btn-secondary:disabled {
      background-color: #bdc3c7;
      cursor: not-allowed;
    }

    .error-message {
      color: #e74c3c;
      font-size: 0.8rem;
      margin-top: 0.5rem;
      padding: 0.5rem;
      background-color: #fdf2f2;
      border: 1px solid #fecaca;
      border-radius: 4px;
    }

    @media (max-width: 768px) {
      .form-row {
        grid-template-columns: 1fr;
      }

      .form-actions {
        flex-direction: column;
      }

      .btn-primary,
      .btn-secondary {
        width: 100%;
      }
    }
  `]
})
export class TaskFormComponent {
  @Input() categories: Category[] = [];
  @Output() taskCreated = new EventEmitter<Task>();
  @Output() cancel = new EventEmitter<void>();

  private taskService = inject(TaskService);

  // Signals for reactive state management
  submitting = signal(false);
  error = signal<string | null>(null);

  // Form data
  formData: TaskCreate = {
    title: '',
    description: '',
    status: 'todo',
    priority: 'medium',
    category_id: undefined,
    due_date: undefined
  };

  onSubmit(): void {
    if (this.submitting()) return;

    this.submitting.set(true);
    this.error.set(null);

    // Prepare the task data
    const taskData: TaskCreate = {
      title: this.formData.title.trim(),
      description: this.formData.description?.trim() || undefined,
      status: this.formData.status,
      priority: this.formData.priority,
      category_id: this.formData.category_id || undefined,
      due_date: this.formData.due_date ? new Date(this.formData.due_date).toISOString() : undefined
    };

    this.taskService.createTask(taskData).subscribe({
      next: (createdTask) => {
        this.submitting.set(false);
        this.taskCreated.emit(createdTask);
        this.resetForm();
      },
      error: (err) => {
        this.submitting.set(false);
        this.error.set('Failed to create task. Please try again.');
        console.error('Error creating task:', err);
      }
    });
  }

  onCancel(): void {
    this.resetForm();
    this.cancel.emit();
  }

  private resetForm(): void {
    this.formData = {
      title: '',
      description: '',
      status: 'todo',
      priority: 'medium',
      category_id: undefined,
      due_date: undefined
    };
    this.error.set(null);
  }
}
