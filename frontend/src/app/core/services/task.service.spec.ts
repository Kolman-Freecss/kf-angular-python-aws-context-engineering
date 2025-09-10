import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { CreateTaskRequest, Task, UpdateTaskRequest } from '../../models/task.model';
import { TaskService } from './task.service';

describe('TaskService', () => {
  let service: TaskService;
  let httpMock: HttpTestingController;

  const mockTask: Task = {
    id: 1,
    title: 'Test Task',
    description: 'Test Description',
    status: 'todo',
    priority: 'medium',
    category_id: 1,
    due_date: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    user_id: 1
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [TaskService]
    });
    service = TestBed.inject(TaskService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  describe('getTasks', () => {
    it('should fetch tasks successfully', () => {
      const mockTasks = [mockTask];
      const mockResponse = { tasks: mockTasks, total: 1, page: 1, per_page: 10 };

      service.getTasks().subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne('/api/tasks');
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });

    it('should fetch tasks with filters', () => {
      const filters = { status: 'todo', priority: 'high', page: 1, per_page: 5 };
      const mockResponse = { tasks: [mockTask], total: 1, page: 1, per_page: 5 };

      service.getTasks(filters).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne('/api/tasks?status=todo&priority=high&page=1&per_page=5');
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });

    it('should handle get tasks error', () => {
      service.getTasks().subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.status).toBe(500);
        }
      });

      const req = httpMock.expectOne('/api/tasks');
      req.flush({}, { status: 500, statusText: 'Internal Server Error' });
    });
  });

  describe('getTask', () => {
    it('should fetch single task successfully', () => {
      service.getTask(1).subscribe(response => {
        expect(response).toEqual(mockTask);
      });

      const req = httpMock.expectOne('/api/tasks/1');
      expect(req.request.method).toBe('GET');
      req.flush(mockTask);
    });

    it('should handle get task error', () => {
      service.getTask(999).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.status).toBe(404);
        }
      });

      const req = httpMock.expectOne('/api/tasks/999');
      req.flush({}, { status: 404, statusText: 'Not Found' });
    });
  });

  describe('createTask', () => {
    it('should create task successfully', () => {
      const createRequest: CreateTaskRequest = {
        title: 'New Task',
        description: 'New Description',
        status: 'todo',
        priority: 'medium',
        category_id: 1
      };

      service.createTask(createRequest).subscribe(response => {
        expect(response).toEqual(mockTask);
      });

      const req = httpMock.expectOne('/api/tasks');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(createRequest);
      req.flush(mockTask);
    });

    it('should handle create task error', () => {
      const createRequest: CreateTaskRequest = {
        title: '',
        description: 'New Description',
        status: 'todo',
        priority: 'medium',
        category_id: 1
      };

      service.createTask(createRequest).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.status).toBe(400);
        }
      });

      const req = httpMock.expectOne('/api/tasks');
      req.flush({ detail: 'Title is required' }, { status: 400, statusText: 'Bad Request' });
    });
  });

  describe('updateTask', () => {
    it('should update task successfully', () => {
      const updateRequest: UpdateTaskRequest = {
        title: 'Updated Task',
        description: 'Updated Description',
        status: 'in_progress',
        priority: 'high'
      };

      const updatedTask = { ...mockTask, ...updateRequest };

      service.updateTask(1, updateRequest).subscribe(response => {
        expect(response).toEqual(updatedTask);
      });

      const req = httpMock.expectOne('/api/tasks/1');
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(updateRequest);
      req.flush(updatedTask);
    });

    it('should handle update task error', () => {
      const updateRequest: UpdateTaskRequest = {
        title: 'Updated Task',
        description: 'Updated Description',
        status: 'in_progress',
        priority: 'high'
      };

      service.updateTask(999, updateRequest).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.status).toBe(404);
        }
      });

      const req = httpMock.expectOne('/api/tasks/999');
      req.flush({}, { status: 404, statusText: 'Not Found' });
    });
  });

  describe('deleteTask', () => {
    it('should delete task successfully', () => {
      service.deleteTask(1).subscribe(response => {
        expect(response).toEqual({ message: 'Task deleted successfully' });
      });

      const req = httpMock.expectOne('/api/tasks/1');
      expect(req.request.method).toBe('DELETE');
      req.flush({ message: 'Task deleted successfully' });
    });

    it('should handle delete task error', () => {
      service.deleteTask(999).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.status).toBe(404);
        }
      });

      const req = httpMock.expectOne('/api/tasks/999');
      req.flush({}, { status: 404, statusText: 'Not Found' });
    });
  });

  describe('getTaskAnalytics', () => {
    it('should fetch task analytics successfully', () => {
      const mockAnalytics = {
        total_tasks: 10,
        completed_tasks: 5,
        pending_tasks: 3,
        in_progress_tasks: 2,
        completion_rate: 50,
        tasks_by_priority: {
          low: 2,
          medium: 5,
          high: 3
        },
        tasks_by_category: {
          'Work': 6,
          'Personal': 4
        }
      };

      service.getTaskAnalytics().subscribe(response => {
        expect(response).toEqual(mockAnalytics);
      });

      const req = httpMock.expectOne('/api/tasks/analytics');
      expect(req.request.method).toBe('GET');
      req.flush(mockAnalytics);
    });

    it('should handle analytics error', () => {
      service.getTaskAnalytics().subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.status).toBe(500);
        }
      });

      const req = httpMock.expectOne('/api/tasks/analytics');
      req.flush({}, { status: 500, statusText: 'Internal Server Error' });
    });
  });
});
