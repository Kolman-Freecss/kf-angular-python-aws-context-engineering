describe('Dashboard', () => {
  beforeEach(() => {
    cy.clearCookies();
    cy.clearLocalStorage();
    cy.register('Test User', 'test@example.com', 'password123');
  });

  describe('Dashboard Overview', () => {
    it('should display welcome message with user name', () => {
      cy.visit('/dashboard');
      
      cy.get('h2').should('contain', 'Welcome to TaskFlow');
      cy.get('p').should('contain', 'Hello, Test User!');
      cy.get('p').should('contain', 'test@example.com');
    });

    it('should show empty state when no tasks exist', () => {
      cy.visit('/dashboard');
      
      cy.get('.empty-state').should('be.visible');
      cy.get('.empty-state').should('contain', 'No tasks yet');
      cy.get('.empty-state a').should('contain', 'Create your first task');
    });
  });

  describe('Task Statistics', () => {
    beforeEach(() => {
      // Create tasks with different statuses
      cy.createTask('Todo Task 1', 'First todo task');
      cy.createTask('Todo Task 2', 'Second todo task');
      cy.createTask('In Progress Task', 'Task in progress');
      cy.createTask('Done Task', 'Completed task');
      
      // Update one task to in progress
      cy.visit('/tasks');
      cy.get('[data-testid="task-status-select"]').eq(1).select('in_progress');
      
      // Update one task to done
      cy.get('[data-testid="task-status-select"]').eq(2).select('done');
    });

    it('should display correct task statistics', () => {
      cy.visit('/dashboard');
      
      // Check total tasks
      cy.get('.stat-number').eq(0).should('contain', '4');
      
      // Check completed tasks
      cy.get('.stat-number').eq(1).should('contain', '1');
      
      // Check in progress tasks
      cy.get('.stat-number').eq(2).should('contain', '1');
      
      // Check pending tasks
      cy.get('.stat-number').eq(3).should('contain', '2');
    });

    it('should display completion rate', () => {
      cy.visit('/dashboard');
      
      // With 1 completed out of 4 total tasks = 25%
      cy.get('.stat-change').should('contain', '25% completion rate');
    });
  });

  describe('Recent Tasks', () => {
    beforeEach(() => {
      // Create multiple tasks
      cy.createTask('Recent Task 1', 'Most recent task');
      cy.createTask('Recent Task 2', 'Second most recent task');
      cy.createTask('Recent Task 3', 'Third most recent task');
      cy.createTask('Recent Task 4', 'Fourth most recent task');
      cy.createTask('Recent Task 5', 'Fifth most recent task');
      cy.createTask('Recent Task 6', 'Sixth most recent task');
    });

    it('should display recent tasks (max 5)', () => {
      cy.visit('/dashboard');
      
      // Should show only the 5 most recent tasks
      cy.get('.task-item').should('have.length', 5);
      
      // Most recent task should be first
      cy.get('.task-title').first().should('contain', 'Recent Task 6');
    });

    it('should display task details correctly', () => {
      cy.visit('/dashboard');
      
      // Check task title
      cy.get('.task-title').first().should('contain', 'Recent Task 6');
      
      // Check task description
      cy.get('.task-description').first().should('contain', 'Sixth most recent task');
      
      // Check task status
      cy.get('.task-status').first().should('contain', 'To Do');
      
      // Check task priority
      cy.get('.task-priority').first().should('contain', 'Medium');
    });

    it('should navigate to tasks page when clicking "View All Tasks"', () => {
      cy.visit('/dashboard');
      
      cy.get('a[href="/tasks"]').click();
      cy.url().should('include', '/tasks');
    });
  });

  describe('Quick Actions', () => {
    it('should navigate to tasks page when clicking "Create New Task"', () => {
      cy.visit('/dashboard');
      
      cy.get('[data-testid="create-task-btn"]').click();
      cy.url().should('include', '/tasks');
    });

    it('should navigate to tasks page when clicking "View All Tasks"', () => {
      cy.visit('/dashboard');
      
      cy.get('[data-testid="view-tasks-btn"]').click();
      cy.url().should('include', '/tasks');
    });
  });

  describe('Category Distribution', () => {
    beforeEach(() => {
      // Create categories
      cy.createCategory('Work', '#3498db');
      cy.createCategory('Personal', '#e74c3c');
      
      // Create tasks with categories
      cy.createTask('Work Task 1', 'First work task');
      cy.createTask('Work Task 2', 'Second work task');
      cy.createTask('Personal Task', 'Personal task');
      
      // Assign categories
      cy.visit('/tasks');
      cy.get('[data-testid="edit-task-btn"]').eq(0).click();
      cy.get('[data-testid="edit-category-select"]').select('Work');
      cy.get('[data-testid="save-task-btn"]').click();
      
      cy.get('[data-testid="edit-task-btn"]').eq(1).click();
      cy.get('[data-testid="edit-category-select"]').select('Work');
      cy.get('[data-testid="save-task-btn"]').click();
      
      cy.get('[data-testid="edit-task-btn"]').eq(2).click();
      cy.get('[data-testid="edit-category-select"]').select('Personal');
      cy.get('[data-testid="save-task-btn"]').click();
    });

    it('should display tasks with categories', () => {
      cy.visit('/dashboard');
      
      // Check that tasks show their categories
      cy.get('.task-category').should('have.length', 3);
      cy.get('.task-category').should('contain', 'Work');
      cy.get('.task-category').should('contain', 'Personal');
    });
  });

  describe('Loading States', () => {
    it('should show loading state while fetching dashboard data', () => {
      // Intercept API call to delay response
      cy.intercept('GET', '/api/tasks*', { delay: 1000 }).as('getTasks');
      
      cy.visit('/dashboard');
      
      cy.get('.loading-state').should('be.visible');
      cy.get('.spinner').should('be.visible');
      cy.get('p').should('contain', 'Loading dashboard...');
      
      cy.wait('@getTasks');
      cy.get('.loading-state').should('not.exist');
    });
  });

  describe('Error States', () => {
    it('should show error state when API fails', () => {
      // Intercept API call to return error
      cy.intercept('GET', '/api/tasks*', { statusCode: 500 }).as('getTasksError');
      
      cy.visit('/dashboard');
      
      cy.wait('@getTasksError');
      cy.get('.error-state').should('be.visible');
      cy.get('.error-state p').should('contain', 'Failed to load dashboard data');
      cy.get('.btn-secondary').should('contain', 'Retry');
    });

    it('should retry loading when retry button is clicked', () => {
      // First request fails
      cy.intercept('GET', '/api/tasks*', { statusCode: 500 }).as('getTasksError');
      cy.visit('/dashboard');
      cy.wait('@getTasksError');
      
      // Second request succeeds
      cy.intercept('GET', '/api/tasks*', { fixture: 'tasks.json' }).as('getTasksSuccess');
      cy.get('.btn-secondary').click();
      cy.wait('@getTasksSuccess');
      
      cy.get('.error-state').should('not.exist');
    });
  });

  describe('Responsive Design', () => {
    it('should adapt to mobile viewport', () => {
      cy.viewport(375, 667); // iPhone SE
      cy.visit('/dashboard');
      
      // Check that layout adapts
      cy.get('.stats-grid').should('be.visible');
      cy.get('.dashboard-content').should('be.visible');
    });

    it('should adapt to tablet viewport', () => {
      cy.viewport(768, 1024); // iPad
      cy.visit('/dashboard');
      
      // Check that layout adapts
      cy.get('.stats-grid').should('be.visible');
      cy.get('.dashboard-content').should('be.visible');
    });
  });
});
