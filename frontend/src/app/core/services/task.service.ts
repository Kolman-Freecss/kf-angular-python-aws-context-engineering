import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Task {
  id: number;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'done';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  due_date?: string;
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
  due_date?: string;
  category_id?: number;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: 'todo' | 'in_progress' | 'done';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  due_date?: string;
  category_id?: number;
}

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
  size: number;
}

@Injectable({
  providedIn: 'root'
})
export class TaskService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/api`;

  // Task methods
  getTasks(page = 1, size = 10, filters?: {
    status?: string;
    priority?: string;
    category_id?: number;
  }): Observable<TaskListResponse> {
    let params: any = { page, size };
    if (filters) {
      Object.assign(params, filters);
    }
    return this.http.get<TaskListResponse>(`${this.apiUrl}/tasks`, { params });
  }

  getTask(id: number): Observable<Task> {
    return this.http.get<Task>(`${this.apiUrl}/tasks/${id}`);
  }

  createTask(task: TaskCreate): Observable<Task> {
    return this.http.post<Task>(`${this.apiUrl}/tasks`, task);
  }

  updateTask(id: number, task: TaskUpdate): Observable<Task> {
    return this.http.put<Task>(`${this.apiUrl}/tasks/${id}`, task);
  }

  deleteTask(id: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/tasks/${id}`);
  }

  updateTaskStatus(id: number, status: 'todo' | 'in_progress' | 'done'): Observable<Task> {
    return this.http.patch<Task>(`${this.apiUrl}/tasks/${id}/status`, { status });
  }

  updateTaskPriority(id: number, priority: 'low' | 'medium' | 'high' | 'urgent'): Observable<Task> {
    return this.http.patch<Task>(`${this.apiUrl}/tasks/${id}/priority`, { priority });
  }

  // Category methods
  getCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(`${this.apiUrl}/categories`);
  }

  createCategory(category: CategoryCreate): Observable<Category> {
    return this.http.post<Category>(`${this.apiUrl}/categories`, category);
  }

  updateCategory(id: number, category: CategoryUpdate): Observable<Category> {
    return this.http.put<Category>(`${this.apiUrl}/categories/${id}`, category);
  }

  deleteCategory(id: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/categories/${id}`);
  }
}
