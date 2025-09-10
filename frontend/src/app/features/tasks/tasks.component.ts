import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-tasks',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="tasks-container">
      <div class="tasks-header">
        <h2>Task Management</h2>
        <button class="btn-primary" (click)="addTask()">
          Add New Task
        </button>
      </div>
      
      <div class="tasks-content">
        <div class="placeholder">
          <h3>Task Management System</h3>
          <p>This feature will be implemented in Phase 2 of the project.</p>
          <p>You'll be able to:</p>
          <ul>
            <li>Create, read, update, and delete tasks</li>
            <li>Categorize tasks by priority and status</li>
            <li>Upload files and attachments</li>
            <li>Set due dates and reminders</li>
            <li>Track task progress</li>
          </ul>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .tasks-container {
      max-width: 1200px;
      margin: 0 auto;
    }
    
    .tasks-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
    }
    
    .tasks-header h2 {
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
      font-size: 1rem;
      transition: background-color 0.3s;
    }
    
    .btn-primary:hover {
      background-color: #2980b9;
    }
    
    .tasks-content {
      background: white;
      padding: 2rem;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .placeholder {
      text-align: center;
      color: #666;
    }
    
    .placeholder h3 {
      color: #2c3e50;
      margin-bottom: 1rem;
    }
    
    .placeholder ul {
      text-align: left;
      max-width: 400px;
      margin: 1rem auto;
    }
    
    .placeholder li {
      margin-bottom: 0.5rem;
    }
  `]
})
export class TasksComponent {
  addTask(): void {
    console.log('Add task functionality will be implemented in Phase 2');
  }
}
