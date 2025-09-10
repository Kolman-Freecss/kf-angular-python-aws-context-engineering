import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="app-container">
      <header class="app-header">
        <h1>TaskFlow</h1>
        <nav>
          <a routerLink="/dashboard" routerLinkActive="active">Dashboard</a>
          <a routerLink="/tasks" routerLinkActive="active">Tasks</a>
          <a routerLink="/categories" routerLinkActive="active">Categories</a>
          <a routerLink="/profile" routerLinkActive="active">Profile</a>
        </nav>
      </header>
      
      <main class="app-main">
        <router-outlet></router-outlet>
      </main>
      
      <footer class="app-footer">
        <p>&copy; 2024 TaskFlow. All rights reserved.</p>
      </footer>
    </div>
  `,
  styles: [`
    .app-container {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    
    .app-header {
      background-color: #2c3e50;
      color: white;
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .app-header h1 {
      margin: 0;
      font-size: 1.5rem;
    }
    
    .app-header nav {
      display: flex;
      gap: 1rem;
    }
    
    .app-header nav a {
      color: white;
      text-decoration: none;
      padding: 0.5rem 1rem;
      border-radius: 4px;
      transition: background-color 0.3s;
    }
    
    .app-header nav a:hover,
    .app-header nav a.active {
      background-color: #34495e;
    }
    
    .app-main {
      flex: 1;
      padding: 2rem;
    }
    
    .app-footer {
      background-color: #ecf0f1;
      padding: 1rem 2rem;
      text-align: center;
      color: #7f8c8d;
    }
  `]
})
export class AppComponent {
  title = 'TaskFlow';
}
