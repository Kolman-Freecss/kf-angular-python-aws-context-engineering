import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="profile-container">
      <div class="profile-header">
        <h2>User Profile</h2>
      </div>
      
      <div class="profile-content">
        <div class="profile-info">
          <div class="info-item">
            <label>Full Name:</label>
            <span>{{ user()?.full_name || 'N/A' }}</span>
          </div>
          
          <div class="info-item">
            <label>Email:</label>
            <span>{{ user()?.email || 'N/A' }}</span>
          </div>
          
          <div class="info-item">
            <label>Status:</label>
            <span class="status" [class.active]="user()?.is_active">
              {{ user()?.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          
          <div class="info-item">
            <label>Member Since:</label>
            <span>{{ formatDate(user()?.created_at) }}</span>
          </div>
        </div>
        
        <div class="profile-actions">
          <button class="btn-secondary" (click)="editProfile()">
            Edit Profile
          </button>
          <button class="btn-danger" (click)="logout()">
            Logout
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .profile-container {
      max-width: 800px;
      margin: 0 auto;
    }
    
    .profile-header {
      margin-bottom: 2rem;
    }
    
    .profile-header h2 {
      margin: 0;
      color: #2c3e50;
    }
    
    .profile-content {
      background: white;
      padding: 2rem;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .profile-info {
      margin-bottom: 2rem;
    }
    
    .info-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem 0;
      border-bottom: 1px solid #ecf0f1;
    }
    
    .info-item:last-child {
      border-bottom: none;
    }
    
    .info-item label {
      font-weight: bold;
      color: #2c3e50;
      min-width: 120px;
    }
    
    .status {
      padding: 0.25rem 0.75rem;
      border-radius: 12px;
      font-size: 0.875rem;
      font-weight: bold;
      background-color: #e74c3c;
      color: white;
    }
    
    .status.active {
      background-color: #27ae60;
    }
    
    .profile-actions {
      display: flex;
      gap: 1rem;
      justify-content: center;
    }
    
    .btn-secondary {
      background-color: #95a5a6;
      color: white;
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 4px;
      cursor: pointer;
      font-size: 1rem;
      transition: background-color 0.3s;
    }
    
    .btn-secondary:hover {
      background-color: #7f8c8d;
    }
    
    .btn-danger {
      background-color: #e74c3c;
      color: white;
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 4px;
      cursor: pointer;
      font-size: 1rem;
      transition: background-color 0.3s;
    }
    
    .btn-danger:hover {
      background-color: #c0392b;
    }
  `]
})
export class ProfileComponent {
  constructor(public authService: AuthService) {
    this.user = authService.user;
  }

  user = this.authService.user;

  formatDate(dateString?: string): string {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  }

  editProfile(): void {
    console.log('Edit profile functionality will be implemented in Phase 2');
  }

  logout(): void {
    this.authService.logout();
  }
}
