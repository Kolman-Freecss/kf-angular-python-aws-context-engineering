import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Category } from '../../../core/services/task.service';

export interface TaskFilters {
  status?: string;
  priority?: string;
  category_id?: number;
}

@Component({
  selector: 'app-task-filters',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="task-filters">
      <div class="filters-header">
        <h4>Filter Tasks</h4>
        <button 
          class="btn-clear" 
          (click)="clearFilters()"
          data-testid="clear-filters-btn">
          Clear All
        </button>
      </div>

      <div class="filters-content">
        <div class="filter-group">
          <label for="status-filter">Status</label>
          <select
            id="status-filter"
            [(ngModel)]="filters.status"
            (ngModelChange)="onFilterChange()"
            data-testid="status-filter">
            <option value="">All Statuses</option>
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
          </select>
        </div>

        <div class="filter-group">
          <label for="priority-filter">Priority</label>
          <select
            id="priority-filter"
            [(ngModel)]="filters.priority"
            (ngModelChange)="onFilterChange()"
            data-testid="priority-filter">
            <option value="">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>

        <div class="filter-group">
          <label for="category-filter">Category</label>
          <select
            id="category-filter"
            [(ngModel)]="filters.category_id"
            (ngModelChange)="onFilterChange()"
            data-testid="category-filter">
            <option value="">All Categories</option>
            <option 
              *ngFor="let category of categories" 
              [value]="category.id">
              {{ category.name }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label for="sort-filter">Sort By</label>
          <select
            id="sort-filter"
            [(ngModel)]="sortBy"
            (ngModelChange)="onFilterChange()"
            data-testid="sort-filter">
            <option value="created_at">Created Date</option>
            <option value="updated_at">Updated Date</option>
            <option value="due_date">Due Date</option>
            <option value="priority">Priority</option>
            <option value="status">Status</option>
            <option value="title">Title</option>
          </select>
        </div>

        <div class="filter-group">
          <label for="sort-order">Order</label>
          <select
            id="sort-order"
            [(ngModel)]="sortOrder"
            (ngModelChange)="onFilterChange()"
            data-testid="sort-order">
            <option value="desc">Descending</option>
            <option value="asc">Ascending</option>
          </select>
        </div>
      </div>

      <div class="active-filters" *ngIf="hasActiveFilters()">
        <span class="active-filters-label">Active filters:</span>
        <div class="filter-tags">
          <span 
            *ngIf="filters.status" 
            class="filter-tag"
            data-testid="active-status-filter">
            Status: {{ getStatusLabel(filters.status) }}
            <button 
              class="remove-filter" 
              (click)="removeFilter('status')"
              data-testid="remove-status-filter">
              ×
            </button>
          </span>
          
          <span 
            *ngIf="filters.priority" 
            class="filter-tag"
            data-testid="active-priority-filter">
            Priority: {{ getPriorityLabel(filters.priority) }}
            <button 
              class="remove-filter" 
              (click)="removeFilter('priority')"
              data-testid="remove-priority-filter">
              ×
            </button>
          </span>
          
          <span 
            *ngIf="filters.category_id" 
            class="filter-tag"
            data-testid="active-category-filter">
            Category: {{ getCategoryName(filters.category_id) }}
            <button 
              class="remove-filter" 
              (click)="removeFilter('category_id')"
              data-testid="remove-category-filter">
              ×
            </button>
          </span>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .task-filters {
      background: white;
      padding: 1rem;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      margin-bottom: 1rem;
    }

    .filters-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }

    .filters-header h4 {
      margin: 0;
      color: #2c3e50;
      font-size: 1rem;
    }

    .btn-clear {
      background-color: #e74c3c;
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.8rem;
      transition: background-color 0.3s;
    }

    .btn-clear:hover {
      background-color: #c0392b;
    }

    .filters-content {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .filter-group {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }

    .filter-group label {
      font-size: 0.8rem;
      color: #7f8c8d;
      font-weight: 500;
    }

    .filter-group select {
      padding: 0.5rem;
      border: 1px solid #bdc3c7;
      border-radius: 4px;
      font-size: 0.9rem;
      background-color: white;
    }

    .filter-group select:focus {
      outline: none;
      border-color: #3498db;
      box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
    }

    .active-filters {
      padding-top: 1rem;
      border-top: 1px solid #ecf0f1;
    }

    .active-filters-label {
      font-size: 0.8rem;
      color: #7f8c8d;
      margin-bottom: 0.5rem;
      display: block;
    }

    .filter-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .filter-tag {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background-color: #3498db;
      color: white;
      padding: 0.25rem 0.5rem;
      border-radius: 12px;
      font-size: 0.8rem;
    }

    .remove-filter {
      background: none;
      border: none;
      color: white;
      cursor: pointer;
      font-size: 1rem;
      line-height: 1;
      padding: 0;
      width: 16px;
      height: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      transition: background-color 0.2s;
    }

    .remove-filter:hover {
      background-color: rgba(255, 255, 255, 0.2);
    }

    @media (max-width: 768px) {
      .filters-content {
        grid-template-columns: 1fr;
      }

      .filters-header {
        flex-direction: column;
        gap: 0.5rem;
        align-items: stretch;
      }

      .btn-clear {
        align-self: flex-end;
      }
    }
  `]
})
export class TaskFiltersComponent {
  @Input() categories: Category[] = [];
  @Output() filtersChanged = new EventEmitter<TaskFilters>();

  // Filter state
  filters: TaskFilters = {};
  sortBy = 'created_at';
  sortOrder = 'desc';

  onFilterChange(): void {
    this.filtersChanged.emit(this.filters);
  }

  clearFilters(): void {
    this.filters = {};
    this.sortBy = 'created_at';
    this.sortOrder = 'desc';
    this.filtersChanged.emit(this.filters);
  }

  removeFilter(filterKey: keyof TaskFilters): void {
    delete this.filters[filterKey];
    this.filtersChanged.emit(this.filters);
  }

  hasActiveFilters(): boolean {
    return Object.keys(this.filters).length > 0;
  }

  getStatusLabel(status: string): string {
    const statusLabels: { [key: string]: string } = {
      'todo': 'To Do',
      'in_progress': 'In Progress',
      'done': 'Done'
    };
    return statusLabels[status] || status;
  }

  getPriorityLabel(priority: string): string {
    const priorityLabels: { [key: string]: string } = {
      'low': 'Low',
      'medium': 'Medium',
      'high': 'High',
      'urgent': 'Urgent'
    };
    return priorityLabels[priority] || priority;
  }

  getCategoryName(categoryId: number): string {
    const category = this.categories.find(c => c.id === categoryId);
    return category ? category.name : 'Unknown';
  }
}
