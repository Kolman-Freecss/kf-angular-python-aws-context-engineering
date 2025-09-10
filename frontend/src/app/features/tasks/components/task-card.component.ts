import { CommonModule } from '@angular/common';
import { Component, EventEmitter, inject, Input, Output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Category, Task, TaskService } from '../../../core/services/task.service';
import { FileUploadComponent } from './file-upload.component';

@Component({
  selector: 'app-task-card',
  standalone: true,
  imports: [CommonModule, FormsModule, FileUploadComponent],
  template: `
    <div class="task-card" [class]="getPriorityClass()">
      <div class="task-header">
        <h3 class="task-title" data-testid="task-title">{{ task.title }}</h3>
        <div class="task-actions">
          <button 
            class="btn-icon" 
            (click)="toggleEdit()"
            data-testid="edit-task-btn"
            [attr.aria-label]="'Edit task: ' + task.title">
            ✏️
          </button>
          <button 
            class="btn-icon btn-danger" 
            (click)="deleteTask()"
            data-testid="delete-task-btn"
            [attr.aria-label]="'Delete task: ' + task.title">
            🗑️
          </button>
        </div>
      </div>

      <div *ngIf="task.description" class="task-description">
        {{ task.description }}
      </div>

      <div class="task-meta">
        <div class="task-status">
          <label>Status:</label>
          <select 
            [value]="task.status" 
            (change)="updateStatus($event)"
            data-testid="task-status-select">
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
          </select>
        </div>

        <div class="task-priority">
          <label>Priority:</label>
          <select 
            [value]="task.priority" 
            (change)="updatePriority($event)"
            data-testid="task-priority-select">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>
      </div>

      <div *ngIf="task.category" class="task-category">
        <span 
          class="category-badge" 
          [style.background-color]="task.category.color"
          data-testid="task-category">
          {{ task.category.name }}
        </span>
      </div>

      <div *ngIf="task.due_date" class="task-due-date">
        <span class="due-date-label">Due:</span>
        <span 
          class="due-date" 
          [class.overdue]="isOverdue()"
          data-testid="task-due-date">
          {{ formatDate(task.due_date) }}
        </span>
      </div>

      <div class="task-dates">
        <small class="created-date">
          Created: {{ formatDate(task.created_at) }}
        </small>
        <small *ngIf="task.updated_at" class="updated-date">
          Updated: {{ formatDate(task.updated_at) }}
        </small>
      </div>

      <!-- Edit Form -->
      <div *ngIf="isEditing()" class="task-edit-form">
        <div class="form-group">
          <label for="edit-title">Title:</label>
          <input 
            id="edit-title"
            type="text" 
            [(ngModel)]="editForm.title"
            data-testid="edit-title-input">
        </div>

        <div class="form-group">
          <label for="edit-description">Description:</label>
          <textarea 
            id="edit-description"
            [(ngModel)]="editForm.description"
            rows="3"
            data-testid="edit-description-input">
          </textarea>
        </div>

        <div class="form-group">
          <label for="edit-category">Category:</label>
          <select 
            id="edit-category"
            [(ngModel)]="editForm.category_id"
            data-testid="edit-category-select">
            <option value="">No Category</option>
            <option 
              *ngFor="let category of categories" 
              [value]="category.id">
              {{ category.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="edit-due-date">Due Date:</label>
          <input 
            id="edit-due-date"
            type="datetime-local" 
            [(ngModel)]="editForm.due_date"
            data-testid="edit-due-date-input">
        </div>

        <div class="form-actions">
          <button 
            class="btn-primary" 
            (click)="saveChanges()"
            data-testid="save-task-btn">
            Save
          </button>
          <button 
            class="btn-secondary" 
            (click)="cancelEdit()"
            data-testid="cancel-edit-btn">
            Cancel
          </button>
        </div>
      </div>

      <!-- File Upload Section -->
      <div class="file-upload-section">
        <app-file-upload 
          [taskId]="task.id"
          (filesUpdated)="onFilesUpdated($event)">
        </app-file-upload>
      </div>
    </div>
  `,
  styles: [`
    .task-card {
      background: white;
      border-radius: 8px;
      padding: 1rem;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      border-left: 4px solid #3498db;
      transition: transform 0.2s, box-shadow 0.2s;
    }

    .task-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }

    .task-card.priority-low {
      border-left-color: #27ae60;
    }

    .task-card.priority-medium {
      border-left-color: #f39c12;
    }

    .task-card.priority-high {
      border-left-color: #e67e22;
    }

    .task-card.priority-urgent {
      border-left-color: #e74c3c;
    }

    .task-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 0.5rem;
    }

    .task-title {
      margin: 0;
      font-size: 1.1rem;
      color: #2c3e50;
      flex: 1;
      margin-right: 1rem;
    }

    .task-actions {
      display: flex;
      gap: 0.5rem;
    }

    .btn-icon {
      background: none;
      border: none;
      cursor: pointer;
      padding: 0.25rem;
      border-radius: 4px;
      font-size: 1rem;
      transition: background-color 0.2s;
    }

    .btn-icon:hover {
      background-color: #ecf0f1;
    }

    .btn-danger:hover {
      background-color: #e74c3c;
      color: white;
    }

    .task-description {
      color: #7f8c8d;
      margin-bottom: 1rem;
      line-height: 1.4;
    }

    .task-meta {
      display: flex;
      gap: 1rem;
      margin-bottom: 1rem;
      flex-wrap: wrap;
    }

    .task-status, .task-priority {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }

    .task-status label, .task-priority label {
      font-size: 0.8rem;
      color: #7f8c8d;
      font-weight: 500;
    }

    .task-status select, .task-priority select {
      padding: 0.25rem 0.5rem;
      border: 1px solid #bdc3c7;
      border-radius: 4px;
      font-size: 0.9rem;
    }

    .task-category {
      margin-bottom: 0.5rem;
    }

    .category-badge {
      display: inline-block;
      padding: 0.25rem 0.5rem;
      border-radius: 12px;
      color: white;
      font-size: 0.8rem;
      font-weight: 500;
    }

    .task-due-date {
      margin-bottom: 0.5rem;
    }

    .due-date-label {
      font-size: 0.8rem;
      color: #7f8c8d;
      margin-right: 0.5rem;
    }

    .due-date {
      font-size: 0.9rem;
      color: #2c3e50;
    }

    .due-date.overdue {
      color: #e74c3c;
      font-weight: 500;
    }

    .task-dates {
      display: flex;
      justify-content: space-between;
      margin-top: 1rem;
      padding-top: 0.5rem;
      border-top: 1px solid #ecf0f1;
    }

    .created-date, .updated-date {
      color: #95a5a6;
      font-size: 0.75rem;
    }

    .task-edit-form {
      margin-top: 1rem;
      padding-top: 1rem;
      border-top: 1px solid #ecf0f1;
    }

    .form-group {
      margin-bottom: 1rem;
    }

    .form-group label {
      display: block;
      margin-bottom: 0.25rem;
      font-size: 0.9rem;
      color: #2c3e50;
      font-weight: 500;
    }

    .form-group input, .form-group textarea, .form-group select {
      width: 100%;
      padding: 0.5rem;
      border: 1px solid #bdc3c7;
      border-radius: 4px;
      font-size: 0.9rem;
    }

    .form-group textarea {
      resize: vertical;
    }

    .form-actions {
      display: flex;
      gap: 0.5rem;
      justify-content: flex-end;
    }

    .btn-primary {
      background-color: #3498db;
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.9rem;
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
    }

    .btn-secondary:hover {
      background-color: #7f8c8d;
    }

    @media (max-width: 768px) {
      .task-meta {
        flex-direction: column;
        gap: 0.5rem;
      }

      .task-dates {
        flex-direction: column;
        gap: 0.25rem;
      }
    }

    .file-upload-section {
      margin-top: 1rem;
      padding-top: 1rem;
      border-top: 1px solid #ecf0f1;
    }
  `]
})
export class TaskCardComponent {
  @Input() task!: Task;
  @Input() categories: Category[] = [];
  @Output() taskUpdated = new EventEmitter<Task>();
  @Output() taskDeleted = new EventEmitter<number>();

  private taskService = inject(TaskService);

  // Signals for reactive state management
  isEditing = signal(false);
  editForm = {
    title: '',
    description: '',
    category_id: null as number | null,
    due_date: ''
  };

  ngOnInit(): void {
    // Initialize edit form with current task data
    this.editForm = {
      title: this.task.title,
      description: this.task.description || '',
      category_id: this.task.category_id || null,
      due_date: this.task.due_date ? this.formatDateForInput(this.task.due_date) : ''
    };
  }

  toggleEdit(): void {
    this.isEditing.set(!this.isEditing());
  }

  cancelEdit(): void {
    this.isEditing.set(false);
    // Reset form to original values
    this.editForm = {
      title: this.task.title,
      description: this.task.description || '',
      category_id: this.task.category_id || null,
      due_date: this.task.due_date ? this.formatDateForInput(this.task.due_date) : ''
    };
  }

  saveChanges(): void {
    const formData = this.editForm;
    const updateData: any = {};

    if (formData.title !== this.task.title) {
      updateData.title = formData.title;
    }
    if (formData.description !== (this.task.description || '')) {
      updateData.description = formData.description;
    }
    if (formData.category_id !== (this.task.category_id || null)) {
      updateData.category_id = formData.category_id;
    }
    if (formData.due_date !== (this.task.due_date ? this.formatDateForInput(this.task.due_date) : '')) {
      updateData.due_date = formData.due_date ? new Date(formData.due_date).toISOString() : null;
    }

    if (Object.keys(updateData).length > 0) {
      this.taskService.updateTask(this.task.id, updateData).subscribe({
        next: (updatedTask) => {
          this.taskUpdated.emit(updatedTask);
          this.isEditing.set(false);
        },
        error: (err) => {
          console.error('Error updating task:', err);
          // You could show an error message here
        }
      });
    } else {
      this.isEditing.set(false);
    }
  }

  updateStatus(event: Event): void {
    const target = event.target as HTMLSelectElement;
    const newStatus = target.value as 'todo' | 'in_progress' | 'done';
    
    this.taskService.updateTaskStatus(this.task.id, newStatus).subscribe({
      next: (updatedTask) => {
        this.taskUpdated.emit(updatedTask);
      },
      error: (err) => {
        console.error('Error updating task status:', err);
        // Reset the select to original value
        target.value = this.task.status;
      }
    });
  }

  updatePriority(event: Event): void {
    const target = event.target as HTMLSelectElement;
    const newPriority = target.value as 'low' | 'medium' | 'high' | 'urgent';
    
    this.taskService.updateTaskPriority(this.task.id, newPriority).subscribe({
      next: (updatedTask) => {
        this.taskUpdated.emit(updatedTask);
      },
      error: (err) => {
        console.error('Error updating task priority:', err);
        // Reset the select to original value
        target.value = this.task.priority;
      }
    });
  }

  deleteTask(): void {
    if (confirm('Are you sure you want to delete this task?')) {
      this.taskService.deleteTask(this.task.id).subscribe({
        next: () => {
          this.taskDeleted.emit(this.task.id);
        },
        error: (err) => {
          console.error('Error deleting task:', err);
          // You could show an error message here
        }
      });
    }
  }

  getPriorityClass(): string {
    return `priority-${this.task.priority}`;
  }

  isOverdue(): boolean {
    if (!this.task.due_date) return false;
    return new Date(this.task.due_date) < new Date();
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString();
  }

  formatDateForInput(dateString: string): string {
    const date = new Date(dateString);
    return date.toISOString().slice(0, 16); // Format for datetime-local input
  }

  onFilesUpdated(files: any[]): void {
    // Files have been updated, could emit an event or update local state
    console.log('Files updated:', files);
  }
}
