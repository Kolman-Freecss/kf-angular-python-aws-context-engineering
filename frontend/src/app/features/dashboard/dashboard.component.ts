import { CommonModule } from '@angular/common';
import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { Task, TaskService } from '../../core/services/task.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="dashboard-container">
      <div class="welcome-section">
        <h2>Welcome to TaskFlow</h2>
        <p>Hello, {{ user()?.full_name || 'User' }}!</p>
        <p>Email: {{ user()?.email }}</p>
      </div>
      
      <!-- Loading State -->
      <div *ngIf="loading()" class="loading-state">
        <div class="spinner"></div>
        <p>Loading dashboard...</p>
      </div>

      <!-- Error State -->
      <div *ngIf="error()" class="error-state">
        <p>{{ error() }}</p>
        <button class="btn-secondary" (click)="loadDashboardData()">Retry</button>
      </div>

      <!-- Dashboard Content -->
      <div *ngIf="!loading() && !error()">
        <div class="stats-grid">
          <div class="stat-card">
            <h3>Total Tasks</h3>
            <div class="stat-number">{{ totalTasks() }}</div>
            <div class="stat-change" [class.positive]="true">
              All your tasks
            </div>
          </div>
          
          <div class="stat-card">
            <h3>Completed</h3>
            <div class="stat-number">{{ completedTasks() }}</div>
            <div class="stat-change" [class.positive]="completionRate() > 50">
              {{ completionRate() }}% completion rate
            </div>
          </div>
          
          <div class="stat-card">
            <h3>In Progress</h3>
            <div class="stat-number">{{ inProgressTasks() }}</div>
            <div class="stat-change">
              Currently working on
            </div>
          </div>
          
          <div class="stat-card">
            <h3>Pending</h3>
            <div class="stat-number">{{ pendingTasks() }}</div>
            <div class="stat-change">
              Waiting to start
            </div>
          </div>
        </div>

        <div class="dashboard-content">
          <div class="recent-tasks">
            <div class="section-header">
              <h3>Recent Tasks</h3>
              <a routerLink="/tasks" class="btn-link">View All Tasks</a>
            </div>
            
            <div *ngIf="recentTasks().length === 0" class="empty-state">
              <p>No tasks yet. <a routerLink="/tasks">Create your first task</a> to get started!</p>
            </div>
            
            <div *ngFor="let task of recentTasks(); trackBy: trackByTaskId" class="task-item">
              <div class="task-info">
                <h4 class="task-title">{{ task.title }}</h4>
                <p class="task-description" *ngIf="task.description">{{ task.description }}</p>
                <div class="task-meta">
                  <span class="task-status" [class]="'status-' + task.status">
                    {{ getStatusLabel(task.status) }}
                  </span>
                  <span class="task-priority" [class]="'priority-' + task.priority">
                    {{ getPriorityLabel(task.priority) }}
                  </span>
                  <span *ngIf="task.category" class="task-category" [style.background-color]="task.category.color">
                    {{ task.category.name }}
                  </span>
                </div>
              </div>
              <div class="task-date">
                <small>{{ formatDate(task.created_at) }}</small>
              </div>
            </div>
          </div>

          <div class="quick-actions">
            <div class="section-header">
              <h3>Quick Actions</h3>
            </div>
            
            <div class="action-buttons">
              <a routerLink="/tasks" class="action-btn primary" data-testid="create-task-btn">
                <span class="action-icon">➕</span>
                <span class="action-text">Create New Task</span>
              </a>
              
              <a routerLink="/tasks" class="action-btn secondary" data-testid="view-tasks-btn">
                <span class="action-icon">📋</span>
                <span class="action-text">View All Tasks</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 1rem;
    }
    
    .welcome-section {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 2rem;
      border-radius: 8px;
      margin-bottom: 2rem;
    }
    
    .welcome-section h2 {
      margin: 0 0 1rem 0;
      font-size: 2rem;
    }
    
    .loading-state, .error-state {
      text-align: center;
      padding: 3rem;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      margin-bottom: 2rem;
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
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1rem;
      margin-bottom: 2rem;
    }
    
    .stat-card {
      background: white;
      padding: 1.5rem;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      text-align: center;
    }
    
    .stat-card h3 {
      margin: 0 0 1rem 0;
      color: #666;
      font-size: 1rem;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    
    .stat-number {
      font-size: 2.5rem;
      font-weight: bold;
      color: #2c3e50;
      margin-bottom: 0.5rem;
    }

    .stat-change {
      font-size: 0.8rem;
      color: #7f8c8d;
    }

    .stat-change.positive {
      color: #27ae60;
    }

    .dashboard-content {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 2rem;
    }

    .recent-tasks, .quick-actions {
      background: white;
      padding: 1.5rem;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }

    .section-header h3 {
      margin: 0;
      color: #2c3e50;
    }

    .btn-link {
      color: #3498db;
      text-decoration: none;
      font-size: 0.9rem;
    }

    .btn-link:hover {
      text-decoration: underline;
    }

    .empty-state {
      text-align: center;
      color: #7f8c8d;
      padding: 2rem;
    }

    .empty-state a {
      color: #3498db;
      text-decoration: none;
    }

    .empty-state a:hover {
      text-decoration: underline;
    }

    .task-item {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding: 1rem;
      border-bottom: 1px solid #ecf0f1;
    }

    .task-item:last-child {
      border-bottom: none;
    }

    .task-info {
      flex: 1;
    }

    .task-title {
      margin: 0 0 0.5rem 0;
      color: #2c3e50;
      font-size: 1rem;
    }

    .task-description {
      margin: 0 0 0.5rem 0;
      color: #7f8c8d;
      font-size: 0.9rem;
    }

    .task-meta {
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
    }

    .task-status, .task-priority, .task-category {
      font-size: 0.8rem;
      padding: 0.25rem 0.5rem;
      border-radius: 12px;
      font-weight: 500;
    }

    .task-status {
      background-color: #ecf0f1;
      color: #2c3e50;
    }

    .task-status.status-done {
      background-color: #d5f4e6;
      color: #27ae60;
    }

    .task-status.status-in_progress {
      background-color: #fef5e7;
      color: #f39c12;
    }

    .task-priority {
      background-color: #e8f4fd;
      color: #3498db;
    }

    .task-priority.priority-high {
      background-color: #fdf2f2;
      color: #e74c3c;
    }

    .task-priority.priority-urgent {
      background-color: #fdf2f2;
      color: #c0392b;
    }

    .task-category {
      color: white;
    }

    .task-date {
      color: #95a5a6;
      font-size: 0.8rem;
    }

    .action-buttons {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .action-btn {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 1rem;
      border-radius: 8px;
      text-decoration: none;
      transition: transform 0.2s, box-shadow 0.2s;
    }

    .action-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }

    .action-btn.primary {
      background-color: #3498db;
      color: white;
    }

    .action-btn.secondary {
      background-color: #95a5a6;
      color: white;
    }

    .action-icon {
      font-size: 1.2rem;
    }

    .action-text {
      font-weight: 500;
    }

    @media (max-width: 768px) {
      .dashboard-content {
        grid-template-columns: 1fr;
      }

      .task-item {
        flex-direction: column;
        gap: 0.5rem;
      }

      .task-meta {
        justify-content: flex-start;
      }
    }
  `]
})
export class DashboardComponent implements OnInit {
  private taskService = inject(TaskService);
  private authService = inject(AuthService);

  // Signals for reactive state management
  private _totalTasks = signal(0);
  private _completedTasks = signal(0);
  private _inProgressTasks = signal(0);
  private _pendingTasks = signal(0);
  private _recentTasks = signal<Task[]>([]);
  private _loading = signal(false);
  private _error = signal<string | null>(null);

  // Computed values
  totalTasks = computed(() => this._totalTasks());
  completedTasks = computed(() => this._completedTasks());
  inProgressTasks = computed(() => this._inProgressTasks());
  pendingTasks = computed(() => this._pendingTasks());
  recentTasks = computed(() => this._recentTasks());
  loading = computed(() => this._loading());
  error = computed(() => this._error());
  completionRate = computed(() => {
    const total = this.totalTasks();
    const completed = this.completedTasks();
    return total > 0 ? Math.round((completed / total) * 100) : 0;
  });

  user = this.authService.user;

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this._loading.set(true);
    this._error.set(null);

    // Load all tasks to calculate statistics
    this.taskService.getTasks(1, 100).subscribe({
      next: (response) => {
        const tasks = response.tasks;
        
        // Calculate statistics
        this._totalTasks.set(tasks.length);
        this._completedTasks.set(tasks.filter(t => t.status === 'done').length);
        this._inProgressTasks.set(tasks.filter(t => t.status === 'in_progress').length);
        this._pendingTasks.set(tasks.filter(t => t.status === 'todo').length);
        
        // Get recent tasks (last 5)
        const recentTasks = tasks
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
          .slice(0, 5);
        this._recentTasks.set(recentTasks);
        
        this._loading.set(false);
      },
      error: (err) => {
        this._error.set('Failed to load dashboard data. Please try again.');
        this._loading.set(false);
        console.error('Error loading dashboard data:', err);
      }
    });
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

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString();
  }

  trackByTaskId(index: number, task: Task): number {
    return task.id;
  }
}
