import { CommonModule } from '@angular/common';
import { Component, computed, signal } from '@angular/core';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="dashboard-container">
      <div class="welcome-section">
        <h2>Welcome to TaskFlow</h2>
        <p>Hello, {{ user()?.full_name || 'User' }}!</p>
        <p>Email: {{ user()?.email }}</p>
      </div>
      
      <div class="stats-grid">
        <div class="stat-card">
          <h3>Total Tasks</h3>
          <div class="stat-number">{{ totalTasks() }}</div>
        </div>
        
        <div class="stat-card">
          <h3>Completed</h3>
          <div class="stat-number">{{ completedTasks() }}</div>
        </div>
        
        <div class="stat-card">
          <h3>In Progress</h3>
          <div class="stat-number">{{ inProgressTasks() }}</div>
        </div>
        
        <div class="stat-card">
          <h3>Pending</h3>
          <div class="stat-number">{{ pendingTasks() }}</div>
        </div>
      </div>
      
      <div class="recent-activity">
        <h3>Recent Activity</h3>
        <p>Task management features will be implemented in Phase 2.</p>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      max-width: 1200px;
      margin: 0 auto;
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
    }
    
    .recent-activity {
      background: white;
      padding: 1.5rem;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .recent-activity h3 {
      margin: 0 0 1rem 0;
      color: #2c3e50;
    }
  `]
})
export class DashboardComponent {
  // Signals for reactive state management
  private _totalTasks = signal(0);
  private _completedTasks = signal(0);
  private _inProgressTasks = signal(0);
  private _pendingTasks = signal(0);

  // Computed values
  totalTasks = computed(() => this._totalTasks());
  completedTasks = computed(() => this._completedTasks());
  inProgressTasks = computed(() => this._inProgressTasks());
  pendingTasks = computed(() => this._pendingTasks());

  constructor(public authService: AuthService) {
    // Get user from auth service
    this.user = authService.user;
  }

  user = this.authService.user;
}
