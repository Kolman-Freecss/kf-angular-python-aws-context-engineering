import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { of, throwError } from 'rxjs';
import { TaskService } from '../../../core/services/task.service';
import { TaskCardComponent } from './task-card.component';
import { TaskFiltersComponent } from './task-filters.component';
import { TaskFormComponent } from './task-form.component';
import { TaskListComponent } from './task-list.component';

describe('TaskListComponent', () => {
  let component: TaskListComponent;
  let fixture: ComponentFixture<TaskListComponent>;
  let taskService: jasmine.SpyObj<TaskService>;

  const mockTask = {
    id: 1,
    title: 'Test Task',
    description: 'Test Description',
    status: 'todo' as 'todo' | 'in_progress' | 'done',
    priority: 'medium' as 'low' | 'medium' | 'high' | 'urgent',
    category_id: 1,
    due_date: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    user_id: 1
  };

  const mockCategory = {
    id: 1,
    name: 'Work',
    color: '#3498db',
    user_id: 1,
    created_at: '2024-01-01T00:00:00Z'
  };

  beforeEach(async () => {
    const taskServiceSpy = jasmine.createSpyObj('TaskService', [
      'getTasks',
      'getCategories',
      'createTask',
      'updateTask',
      'deleteTask'
    ]);

    await TestBed.configureTestingModule({
      imports: [FormsModule, RouterModule],
      declarations: [
        TaskListComponent,
        TaskCardComponent,
        TaskFiltersComponent,
        TaskFormComponent
      ],
      providers: [
        { provide: TaskService, useValue: taskServiceSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(TaskListComponent);
    component = fixture.componentInstance;
    taskService = TestBed.inject(TaskService) as jasmine.SpyObj<TaskService>;
  });

  beforeEach(() => {
    // Setup default mocks
    taskService.getTasks.and.returnValue(of({
      tasks: [mockTask],
      total: 1,
      page: 1,
      per_page: 10
    }));
    taskService.getCategories.and.returnValue(of([mockCategory]));
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Component Initialization', () => {
    it('should load tasks and categories on init', () => {
      component.ngOnInit();

      expect(taskService.getTasks).toHaveBeenCalledWith(1, 10, {});
      expect(taskService.getCategories).toHaveBeenCalled();
    });

    it('should set initial state correctly', () => {
      expect(component.tasks()).toEqual([]);
      expect(component.categories()).toEqual([]);
      expect(component.loading()).toBe(false);
      expect(component.error()).toBeNull();
      expect(component.showCreateForm()).toBe(false);
      expect(component.currentPage()).toBe(1);
      expect(component.totalTasks()).toBe(0);
    });
  });

  describe('Task Loading', () => {
    it('should load tasks successfully', () => {
      const mockResponse = {
        tasks: [mockTask],
        total: 1,
        page: 1,
        per_page: 10
      };
      taskService.getTasks.and.returnValue(of(mockResponse));

      component.loadTasks();

      expect(component.tasks()).toEqual([mockTask]);
      expect(component.totalTasks()).toBe(1);
      expect(component.loading()).toBe(false);
      expect(component.error()).toBeNull();
    });

    it('should handle task loading error', () => {
      taskService.getTasks.and.returnValue(throwError(() => new Error('API Error')));

      component.loadTasks();

      expect(component.error()).toBe('Failed to load tasks. Please try again.');
      expect(component.loading()).toBe(false);
    });

    it('should set loading state during task loading', () => {
      taskService.getTasks.and.returnValue(of({
        tasks: [mockTask],
        total: 1,
        page: 1,
        per_page: 10
      }));

      component.loadTasks();

      expect(component.loading()).toBe(false); // Should be false after completion
    });
  });

  describe('Category Loading', () => {
    it('should load categories successfully', () => {
      const mockCategories = [mockCategory];
      taskService.getCategories.and.returnValue(of(mockCategories));

      component.loadCategories();

      expect(component.categories()).toEqual(mockCategories);
    });

    it('should handle category loading error', () => {
      taskService.getCategories.and.returnValue(throwError(() => new Error('API Error')));

      component.loadCategories();

      // Should not set error state for categories
      expect(component.error()).toBeNull();
    });
  });

  describe('Task Management', () => {
    beforeEach(() => {
      component.tasks.set([mockTask]);
    });

    it('should handle task creation', () => {
      const newTask = { ...mockTask, id: 2, title: 'New Task' };
      taskService.getTasks.and.returnValue(of({
        tasks: [mockTask, newTask],
        total: 2,
        page: 1,
        per_page: 10
      }));

      component.onTaskCreated(newTask);

      expect(component.showCreateForm()).toBe(false);
      expect(taskService.getTasks).toHaveBeenCalled();
    });

    it('should handle task update', () => {
      const updatedTask = { ...mockTask, title: 'Updated Task' };
      component.tasks.set([mockTask]);

      component.onTaskUpdated(updatedTask);

      expect(component.tasks()).toEqual([updatedTask]);
    });

    it('should handle task deletion', () => {
      component.tasks.set([mockTask]);
      component.totalTasks.set(1);

      component.onTaskDeleted(1);

      expect(component.tasks()).toEqual([]);
      expect(component.totalTasks()).toBe(0);
    });
  });

  describe('Filtering', () => {
    it('should handle filter changes', () => {
      const filters = { status: 'todo', priority: 'high' };
      taskService.getTasks.and.returnValue(of({
        tasks: [mockTask],
        total: 1,
        page: 1,
        per_page: 10
      }));

      component.onFiltersChanged(filters);

      expect(component.currentFilters()).toEqual(filters);
      expect(component.currentPage()).toBe(1);
      expect(taskService.getTasks).toHaveBeenCalledWith(1, 10, filters);
    });
  });

  describe('Pagination', () => {
    beforeEach(() => {
      component.totalTasks.set(25);
      component.pageSize.set(10);
    });

    it('should calculate total pages correctly', () => {
      expect(component.totalPages()).toBe(3);
    });

    it('should navigate to valid page', () => {
      taskService.getTasks.and.returnValue(of({
        tasks: [mockTask],
        total: 25,
        page: 2,
        per_page: 10
      }));

      component.goToPage(2);

      expect(component.currentPage()).toBe(2);
      expect(taskService.getTasks).toHaveBeenCalledWith(2, 10, {});
    });

    it('should not navigate to invalid page', () => {
      const initialPage = component.currentPage();
      
      component.goToPage(0);
      expect(component.currentPage()).toBe(initialPage);
      
      component.goToPage(5);
      expect(component.currentPage()).toBe(initialPage);
    });
  });

  describe('Track By Function', () => {
    it('should track tasks by id', () => {
      expect(component.trackByTaskId(0, mockTask)).toBe(1);
    });
  });

  describe('Template Rendering', () => {
    it('should show create form when showCreateForm is true', () => {
      component.showCreateForm.set(true);
      fixture.detectChanges();

      const formContainer = fixture.debugElement.nativeElement.querySelector('.task-form-container');
      expect(formContainer).toBeTruthy();
    });

    it('should hide create form when showCreateForm is false', () => {
      component.showCreateForm.set(false);
      fixture.detectChanges();

      const formContainer = fixture.debugElement.nativeElement.querySelector('.task-form-container');
      expect(formContainer).toBeFalsy();
    });

    it('should show loading state when loading', () => {
      component.loading.set(true);
      fixture.detectChanges();

      const loadingState = fixture.debugElement.nativeElement.querySelector('.loading-state');
      expect(loadingState).toBeTruthy();
    });

    it('should show error state when error exists', () => {
      component.error.set('Test error');
      fixture.detectChanges();

      const errorState = fixture.debugElement.nativeElement.querySelector('.error-state');
      expect(errorState).toBeTruthy();
      expect(errorState.textContent).toContain('Test error');
    });

    it('should show empty state when no tasks', () => {
      component.tasks.set([]);
      component.loading.set(false);
      component.error.set(null);
      fixture.detectChanges();

      const emptyState = fixture.debugElement.nativeElement.querySelector('.empty-state');
      expect(emptyState).toBeTruthy();
    });

    it('should show pagination when tasks exist', () => {
      component.tasks.set([mockTask]);
      component.totalTasks.set(1);
      component.loading.set(false);
      component.error.set(null);
      fixture.detectChanges();

      const pagination = fixture.debugElement.nativeElement.querySelector('.pagination');
      expect(pagination).toBeTruthy();
    });
  });

  describe('Button Interactions', () => {
    it('should toggle create form visibility', () => {
      expect(component.showCreateForm()).toBe(false);
      
      const addButton = fixture.debugElement.nativeElement.querySelector('[data-testid="add-task-btn"]');
      addButton.click();
      
      expect(component.showCreateForm()).toBe(true);
    });

    it('should retry loading tasks on retry button click', () => {
      component.error.set('Test error');
      fixture.detectChanges();

      const retryButton = fixture.debugElement.nativeElement.querySelector('.btn-secondary');
      retryButton.click();

      expect(taskService.getTasks).toHaveBeenCalled();
    });
  });
});
