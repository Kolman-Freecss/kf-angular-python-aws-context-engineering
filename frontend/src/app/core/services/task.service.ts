import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, of } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { CacheService } from './cache.service';

export interface Task {
  id: number;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'done';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  due_date?: string | null;
  category_id?: number;
  user_id: number;
  created_at: string;
  updated_at?: string;
  category?: Category;
}

export interface Category {
  id: number;
  name: string;
  color: string;
  user_id: number;
  created_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  status?: 'todo' | 'in_progress' | 'done';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  due_date?: string | null;
  category_id?: number;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: 'todo' | 'in_progress' | 'done';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  due_date?: string | null;
  category_id?: number;
}

// Type aliases for backward compatibility
export type CreateTaskRequest = TaskCreate;
export type UpdateTaskRequest = TaskUpdate;

export interface CategoryCreate {
  name: string;
  color?: string;
}

export interface CategoryUpdate {
  name?: string;
  color?: string;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
  page: number;
  per_page: number;
}

@Injectable({
  providedIn: 'root'
})
export class TaskService {
  private http = inject(HttpClient);
  private cache = inject(CacheService);
  private apiUrl = `${environment.apiUrl}/api`;

  // Task methods
  getTasks(page = 1, size = 10, filters?: {
    status?: string;
    priority?: string;
    category_id?: number;
  }): Observable<TaskListResponse> {
    // Create cache key based on parameters
    const cacheKey = `tasks_${page}_${size}_${JSON.stringify(filters || {})}`;
    
    // Check cache first
    const cachedData = this.cache.get<TaskListResponse>(cacheKey);
    if (cachedData) {
      return of(cachedData);
    }

    // If not in cache, fetch from API
    let params: any = { page, size };
    if (filters) {
      Object.assign(params, filters);
    }
    
    return this.http.get<TaskListResponse>(`${this.apiUrl}/tasks`, { params })
      .pipe(
        tap(data => {
          // Cache the result for 2 minutes
          this.cache.set(cacheKey, data, 2);
        })
      );
  }

  getTask(id: number): Observable<Task> {
    const cacheKey = `task_${id}`;
    
    // Check cache first
    const cachedData = this.cache.get<Task>(cacheKey);
    if (cachedData) {
      return of(cachedData);
    }

    return this.http.get<Task>(`${this.apiUrl}/tasks/${id}`)
      .pipe(
        tap(data => {
          // Cache individual task for 5 minutes
          this.cache.set(cacheKey, data, 5);
        })
      );
  }

  createTask(task: TaskCreate): Observable<Task> {
    return this.http.post<Task>(`${this.apiUrl}/tasks`, task)
      .pipe(
        tap(() => {
          // Invalidate task list cache when creating new task
          this.invalidateTaskListCache();
        })
      );
  }

  updateTask(id: number, task: TaskUpdate): Observable<Task> {
    return this.http.put<Task>(`${this.apiUrl}/tasks/${id}`, task)
      .pipe(
        tap(() => {
          // Invalidate caches when updating task
          this.invalidateTaskListCache();
          this.cache.delete(`task_${id}`);
        })
      );
  }

  deleteTask(id: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/tasks/${id}`)
      .pipe(
        tap(() => {
          // Invalidate caches when deleting task
          this.invalidateTaskListCache();
          this.cache.delete(`task_${id}`);
        })
      );
  }

  updateTaskStatus(id: number, status: 'todo' | 'in_progress' | 'done'): Observable<Task> {
    return this.http.patch<Task>(`${this.apiUrl}/tasks/${id}/status`, { status })
      .pipe(
        tap(() => {
          this.invalidateTaskListCache();
          this.cache.delete(`task_${id}`);
        })
      );
  }

  updateTaskPriority(id: number, priority: 'low' | 'medium' | 'high' | 'urgent'): Observable<Task> {
    return this.http.patch<Task>(`${this.apiUrl}/tasks/${id}/priority`, { priority })
      .pipe(
        tap(() => {
          this.invalidateTaskListCache();
          this.cache.delete(`task_${id}`);
        })
      );
  }

  // Category methods
  getCategories(): Observable<Category[]> {
    const cacheKey = 'categories';
    
    // Check cache first
    const cachedData = this.cache.get<Category[]>(cacheKey);
    if (cachedData) {
      return of(cachedData);
    }

    return this.http.get<Category[]>(`${this.apiUrl}/categories`)
      .pipe(
        tap(data => {
          // Cache categories for 10 minutes
          this.cache.set(cacheKey, data, 10);
        })
      );
  }

  createCategory(category: CategoryCreate): Observable<Category> {
    return this.http.post<Category>(`${this.apiUrl}/categories`, category)
      .pipe(
        tap(() => {
          // Invalidate categories cache
          this.cache.delete('categories');
        })
      );
  }

  updateCategory(id: number, category: CategoryUpdate): Observable<Category> {
    return this.http.put<Category>(`${this.apiUrl}/categories/${id}`, category)
      .pipe(
        tap(() => {
          // Invalidate categories cache
          this.cache.delete('categories');
        })
      );
  }

  deleteCategory(id: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/categories/${id}`)
      .pipe(
        tap(() => {
          // Invalidate categories cache
          this.cache.delete('categories');
        })
      );
  }

  // Analytics methods
  getTaskAnalytics(): Observable<any> {
    const cacheKey = 'task_analytics';
    
    // Check cache first
    const cachedData = this.cache.get<any>(cacheKey);
    if (cachedData) {
      return of(cachedData);
    }

    return this.http.get<any>(`${this.apiUrl}/tasks/analytics`)
      .pipe(
        tap(data => {
          // Cache analytics for 5 minutes
          this.cache.set(cacheKey, data, 5);
        })
      );
  }

  // Cache invalidation helper
  private invalidateTaskListCache(): void {
    // Clear all task list related cache entries
    const keys = Array.from(this.cache['cache'].keys());
    keys.forEach(key => {
      if (key.startsWith('tasks_')) {
        this.cache.delete(key);
      }
    });
  }
}
