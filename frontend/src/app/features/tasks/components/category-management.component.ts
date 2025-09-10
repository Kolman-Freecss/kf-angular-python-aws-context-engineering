import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Category, CategoryCreate, CategoryUpdate, TaskService } from '../../../core/services/task.service';

@Component({
  selector: 'app-category-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="category-management">
      <div class="category-header">
        <h3>Manage Categories</h3>
        <button 
          class="btn-primary" 
          (click)="showCreateForm.set(!showCreateForm())"
          data-testid="add-category-btn">
          {{ showCreateForm() ? 'Cancel' : 'Add New Category' }}
        </button>
      </div>

      <!-- Create Category Form -->
      <div *ngIf="showCreateForm()" class="category-form">
        <form (ngSubmit)="createCategory()" #categoryForm="ngForm">
          <div class="form-group">
            <label for="category-name">Category Name</label>
            <input
              id="category-name"
              type="text"
              [(ngModel)]="newCategory.name"
              name="categoryName"
              required
              maxlength="100"
              data-testid="category-name-input"
              #nameInput="ngModel">
            <div *ngIf="nameInput.invalid && nameInput.touched" class="error-message">
              Category name is required and must be less than 100 characters.
            </div>
          </div>

          <div class="form-group">
            <label for="category-color">Color</label>
            <div class="color-input-group">
              <input
                id="category-color"
                type="color"
                [(ngModel)]="newCategory.color"
                name="categoryColor"
                data-testid="category-color-input">
              <input
                type="text"
                [(ngModel)]="newCategory.color"
                name="categoryColorText"
                placeholder="#3498db"
                pattern="^#[0-9A-Fa-f]{6}$"
                data-testid="category-color-text-input">
            </div>
          </div>

          <div class="form-actions">
            <button
              type="submit"
              class="btn-primary"
              [disabled]="categoryForm.invalid || creating()"
              data-testid="create-category-btn">
              {{ creating() ? 'Creating...' : 'Create Category' }}
            </button>
            
            <button
              type="button"
              class="btn-secondary"
              (click)="cancelCreate()"
              [disabled]="creating()"
              data-testid="cancel-create-category-btn">
              Cancel
            </button>
          </div>

          <div *ngIf="error()" class="error-message">
            {{ error() }}
          </div>
        </form>
      </div>

      <!-- Categories List -->
      <div class="categories-list">
        <div *ngIf="loading()" class="loading-state">
          <div class="spinner"></div>
          <p>Loading categories...</p>
        </div>

        <div *ngIf="!loading() && categories().length === 0" class="empty-state">
          <p>No categories yet. Create your first category to organize your tasks!</p>
        </div>

        <div *ngFor="let category of categories(); trackBy: trackByCategoryId" class="category-item">
          <div class="category-info">
            <div class="category-color" [style.background-color]="category.color"></div>
            <div class="category-details">
              <h4 class="category-name">{{ category.name }}</h4>
              <small class="category-date">Created: {{ formatDate(category.created_at) }}</small>
            </div>
          </div>

          <div class="category-actions">
            <button 
              class="btn-icon" 
              (click)="editCategory(category)"
              data-testid="edit-category-btn"
              [attr.aria-label]="'Edit category: ' + category.name">
              ✏️
            </button>
            <button 
              class="btn-icon btn-danger" 
              (click)="deleteCategory(category)"
              data-testid="delete-category-btn"
              [attr.aria-label]="'Delete category: ' + category.name">
              🗑️
            </button>
          </div>

          <!-- Edit Form -->
          <div *ngIf="editingCategory()?.id === category.id" class="category-edit-form">
            <form (ngSubmit)="updateCategory(category)" #editForm="ngForm">
              <div class="form-group">
                <label for="edit-name">Category Name</label>
                <input
                  id="edit-name"
                  type="text"
                  [(ngModel)]="editFormData.name"
                  name="editName"
                  required
                  maxlength="100"
                  data-testid="edit-category-name-input">
              </div>

              <div class="form-group">
                <label for="edit-color">Color</label>
                <div class="color-input-group">
                  <input
                    id="edit-color"
                    type="color"
                    [(ngModel)]="editFormData.color"
                    name="editColor"
                    data-testid="edit-category-color-input">
                  <input
                    type="text"
                    [(ngModel)]="editFormData.color"
                    name="editColorText"
                    placeholder="#3498db"
                    pattern="^#[0-9A-Fa-f]{6}$"
                    data-testid="edit-category-color-text-input">
                </div>
              </div>

              <div class="form-actions">
                <button
                  type="submit"
                  class="btn-primary"
                  [disabled]="editForm.invalid || updating()"
                  data-testid="save-category-btn">
                  {{ updating() ? 'Saving...' : 'Save' }}
                </button>
                
                <button
                  type="button"
                  class="btn-secondary"
                  (click)="cancelEdit()"
                  [disabled]="updating()"
                  data-testid="cancel-edit-category-btn">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .category-management {
      background: white;
      padding: 1.5rem;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .category-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
    }

    .category-header h3 {
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
      font-size: 0.9rem;
      font-weight: 500;
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
    }

    .btn-secondary:hover:not(:disabled) {
      background-color: #7f8c8d;
    }

    .btn-secondary:disabled {
      background-color: #bdc3c7;
      cursor: not-allowed;
    }

    .btn-icon {
      background: none;
      border: none;
      cursor: pointer;
      padding: 0.5rem;
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

    .category-form, .category-edit-form {
      background: #f8f9fa;
      padding: 1rem;
      border-radius: 8px;
      margin-bottom: 1.5rem;
    }

    .form-group {
      margin-bottom: 1rem;
    }

    .form-group label {
      display: block;
      margin-bottom: 0.5rem;
      font-weight: 500;
      color: #2c3e50;
      font-size: 0.9rem;
    }

    .form-group input {
      width: 100%;
      padding: 0.75rem;
      border: 1px solid #bdc3c7;
      border-radius: 4px;
      font-size: 0.9rem;
    }

    .form-group input:focus {
      outline: none;
      border-color: #3498db;
      box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
    }

    .color-input-group {
      display: flex;
      gap: 0.5rem;
    }

    .color-input-group input[type="color"] {
      width: 60px;
      height: 40px;
      padding: 0;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }

    .color-input-group input[type="text"] {
      flex: 1;
    }

    .form-actions {
      display: flex;
      gap: 1rem;
      justify-content: flex-end;
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

    .loading-state, .empty-state {
      text-align: center;
      padding: 2rem;
      color: #7f8c8d;
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

    .categories-list {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .category-item {
      border: 1px solid #ecf0f1;
      border-radius: 8px;
      padding: 1rem;
      transition: box-shadow 0.2s;
    }

    .category-item:hover {
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .category-info {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .category-color {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      border: 2px solid #fff;
      box-shadow: 0 0 0 1px #bdc3c7;
    }

    .category-details {
      flex: 1;
    }

    .category-name {
      margin: 0 0 0.25rem 0;
      color: #2c3e50;
      font-size: 1.1rem;
    }

    .category-date {
      color: #7f8c8d;
      font-size: 0.8rem;
    }

    .category-actions {
      display: flex;
      gap: 0.5rem;
      justify-content: flex-end;
    }

    .category-edit-form {
      margin-top: 1rem;
      padding-top: 1rem;
      border-top: 1px solid #ecf0f1;
    }

    @media (max-width: 768px) {
      .category-header {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
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
export class CategoryManagementComponent implements OnInit {
  private taskService = inject(TaskService);

  // Signals for reactive state management
  categories = signal<Category[]>([]);
  loading = signal(false);
  error = signal<string | null>(null);
  showCreateForm = signal(false);
  creating = signal(false);
  editingCategory = signal<Category | null>(null);
  updating = signal(false);

  // Form data
  newCategory: CategoryCreate = {
    name: '',
    color: '#3498db'
  };

  editFormData: CategoryUpdate = {
    name: '',
    color: '#3498db'
  };

  ngOnInit(): void {
    this.loadCategories();
  }

  loadCategories(): void {
    this.loading.set(true);
    this.error.set(null);

    this.taskService.getCategories().subscribe({
      next: (categories) => {
        this.categories.set(categories);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Failed to load categories. Please try again.');
        this.loading.set(false);
        console.error('Error loading categories:', err);
      }
    });
  }

  createCategory(): void {
    if (this.creating()) return;

    this.creating.set(true);
    this.error.set(null);

    this.taskService.createCategory(this.newCategory).subscribe({
      next: (createdCategory) => {
        this.categories.set([...this.categories(), createdCategory]);
        this.newCategory = { name: '', color: '#3498db' };
        this.showCreateForm.set(false);
        this.creating.set(false);
      },
      error: (err) => {
        this.error.set('Failed to create category. Please try again.');
        this.creating.set(false);
        console.error('Error creating category:', err);
      }
    });
  }

  cancelCreate(): void {
    this.showCreateForm.set(false);
    this.newCategory = { name: '', color: '#3498db' };
    this.error.set(null);
  }

  editCategory(category: Category): void {
    this.editingCategory.set(category);
    this.editFormData = {
      name: category.name,
      color: category.color
    };
  }

  updateCategory(category: Category): void {
    if (this.updating()) return;

    this.updating.set(true);
    this.error.set(null);

    this.taskService.updateCategory(category.id, this.editFormData).subscribe({
      next: (updatedCategory) => {
        const currentCategories = this.categories();
        const index = currentCategories.findIndex(c => c.id === category.id);
        if (index !== -1) {
          const updatedCategories = [...currentCategories];
          updatedCategories[index] = updatedCategory;
          this.categories.set(updatedCategories);
        }
        this.editingCategory.set(null);
        this.updating.set(false);
      },
      error: (err) => {
        this.error.set('Failed to update category. Please try again.');
        this.updating.set(false);
        console.error('Error updating category:', err);
      }
    });
  }

  cancelEdit(): void {
    this.editingCategory.set(null);
    this.error.set(null);
  }

  deleteCategory(category: Category): void {
    if (confirm(`Are you sure you want to delete the category "${category.name}"? This action cannot be undone.`)) {
      this.taskService.deleteCategory(category.id).subscribe({
        next: () => {
          const currentCategories = this.categories();
          const filteredCategories = currentCategories.filter(c => c.id !== category.id);
          this.categories.set(filteredCategories);
        },
        error: (err) => {
          this.error.set('Failed to delete category. Please try again.');
          console.error('Error deleting category:', err);
        }
      });
    }
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString();
  }

  trackByCategoryId(index: number, category: Category): number {
    return category.id;
  }
}
