describe('Complete User Journey', () => {
  beforeEach(() => {
    cy.clearCookies();
    cy.clearLocalStorage();
  });

  it('should complete full user workflow from registration to task management', () => {
    // Step 1: User Registration
    cy.visit('/auth/register');
    cy.get('[data-testid="full-name-input"]').type('John Doe');
    cy.get('[data-testid="email-input"]').type('john@example.com');
    cy.get('[data-testid="password-input"]').type('password123');
    cy.get('[data-testid="confirm-password-input"]').type('password123');
    cy.get('[data-testid="register-btn"]').click();
    
    // Should redirect to dashboard
    cy.url().should('include', '/dashboard');
    cy.get('h2').should('contain', 'Welcome to TaskFlow');
    cy.get('p').should('contain', 'Hello, John Doe!');

    // Step 2: Create Categories
    cy.visit('/categories');
    cy.get('[data-testid="add-category-btn"]').click();
    cy.get('[data-testid="category-name-input"]').type('Work');
    cy.get('[data-testid="category-color-input"]').clear().type('#3498db');
    cy.get('[data-testid="create-category-btn"]').click();
    
    cy.get('[data-testid="add-category-btn"]').click();
    cy.get('[data-testid="category-name-input"]').type('Personal');
    cy.get('[data-testid="category-color-input"]').clear().type('#e74c3c');
    cy.get('[data-testid="create-category-btn"]').click();
    
    // Verify categories were created
    cy.get('[data-testid="category-name"]').should('have.length', 2);

    // Step 3: Create Tasks
    cy.visit('/tasks');
    
    // Create Work Task
    cy.get('[data-testid="add-task-btn"]').click();
    cy.get('[data-testid="task-title-input"]').type('Complete Project Proposal');
    cy.get('[data-testid="task-description-input"]').type('Write and submit the project proposal for Q1');
    cy.get('[data-testid="task-status-select"]').select('todo');
    cy.get('[data-testid="task-priority-select"]').select('high');
    cy.get('[data-testid="task-category-select"]').select('Work');
    cy.get('[data-testid="create-task-btn"]').click();
    
    // Create Personal Task
    cy.get('[data-testid="add-task-btn"]').click();
    cy.get('[data-testid="task-title-input"]').type('Buy Groceries');
    cy.get('[data-testid="task-description-input"]').type('Get milk, bread, and vegetables');
    cy.get('[data-testid="task-status-select"]').select('todo');
    cy.get('[data-testid="task-priority-select"]').select('medium');
    cy.get('[data-testid="task-category-select"]').select('Personal');
    cy.get('[data-testid="create-task-btn"]').click();
    
    // Create Another Work Task
    cy.get('[data-testid="add-task-btn"]').click();
    cy.get('[data-testid="task-title-input"]').type('Team Meeting');
    cy.get('[data-testid="task-description-input"]').type('Weekly team standup meeting');
    cy.get('[data-testid="task-status-select"]').select('in_progress');
    cy.get('[data-testid="task-priority-select"]').select('medium');
    cy.get('[data-testid="task-category-select"]').select('Work');
    cy.get('[data-testid="create-task-btn"]').click();

    // Step 4: Verify Tasks Created
    cy.get('[data-testid="task-title"]').should('have.length', 3);
    cy.get('[data-testid="task-title"]').should('contain', 'Complete Project Proposal');
    cy.get('[data-testid="task-title"]').should('contain', 'Buy Groceries');
    cy.get('[data-testid="task-title"]').should('contain', 'Team Meeting');

    // Step 5: Update Task Status
    cy.get('[data-testid="task-status-select"]').eq(0).select('in_progress'); // Project Proposal
    cy.get('[data-testid="task-status-select"]').eq(1).select('done'); // Buy Groceries

    // Step 6: Filter Tasks
    cy.get('[data-testid="status-filter"]').select('done');
    cy.get('[data-testid="task-title"]').should('have.length', 1);
    cy.get('[data-testid="task-title"]').should('contain', 'Buy Groceries');
    
    cy.get('[data-testid="clear-filters-btn"]').click();
    cy.get('[data-testid="task-title"]').should('have.length', 3);

    // Step 7: Filter by Category
    cy.get('[data-testid="category-filter"]').select('Work');
    cy.get('[data-testid="task-title"]').should('have.length', 2);
    cy.get('[data-testid="task-category"]').should('contain', 'Work');

    // Step 8: Upload Files to Task
    cy.get('[data-testid="clear-filters-btn"]').click();
    
    // Upload file to first task
    const fileName = 'project-requirements.pdf';
    const fileContent = 'Project requirements document content';
    
    cy.get('[data-testid="file-input"]').first().selectFile({
      contents: Cypress.Buffer.from(fileContent),
      fileName: fileName,
      mimeType: 'application/pdf'
    });
    
    // Wait for upload to complete
    cy.get('.file-item', { timeout: 10000 }).should('be.visible');
    cy.get('.file-name').should('contain', fileName);

    // Step 9: Edit Task
    cy.get('[data-testid="edit-task-btn"]').first().click();
    cy.get('[data-testid="edit-title-input"]').clear().type('Complete Project Proposal - Updated');
    cy.get('[data-testid="edit-description-input"]').clear().type('Write and submit the project proposal for Q1 with updated requirements');
    cy.get('[data-testid="save-task-btn"]').click();
    
    // Verify changes
    cy.get('[data-testid="task-title"]').first().should('contain', 'Complete Project Proposal - Updated');

    // Step 10: Check Dashboard Statistics
    cy.visit('/dashboard');
    
    // Should show correct statistics
    cy.get('.stat-number').eq(0).should('contain', '3'); // Total tasks
    cy.get('.stat-number').eq(1).should('contain', '1'); // Completed tasks
    cy.get('.stat-number').eq(2).should('contain', '2'); // In progress tasks
    cy.get('.stat-number').eq(3).should('contain', '0'); // Pending tasks
    
    // Should show completion rate
    cy.get('.stat-change').should('contain', '33% completion rate');
    
    // Should show recent tasks
    cy.get('.task-item').should('have.length', 3);
    cy.get('.task-title').first().should('contain', 'Team Meeting'); // Most recent

    // Step 11: Delete a Task
    cy.visit('/tasks');
    cy.get('[data-testid="delete-task-btn"]').eq(1).click(); // Delete "Buy Groceries"
    cy.on('window:confirm', () => true);
    
    // Verify task was deleted
    cy.get('[data-testid="task-title"]').should('have.length', 2);
    cy.get('[data-testid="task-title"]').should('not.contain', 'Buy Groceries');

    // Step 12: Check Updated Dashboard
    cy.visit('/dashboard');
    
    // Statistics should be updated
    cy.get('.stat-number').eq(0).should('contain', '2'); // Total tasks
    cy.get('.stat-number').eq(1).should('contain', '0'); // Completed tasks
    cy.get('.stat-number').eq(2).should('contain', '2'); // In progress tasks
    
    // Should show updated completion rate
    cy.get('.stat-change').should('contain', '0% completion rate');

    // Step 13: Edit Category
    cy.visit('/categories');
    cy.get('[data-testid="edit-category-btn"]').first().click();
    cy.get('[data-testid="edit-category-name-input"]').clear().type('Work Projects');
    cy.get('[data-testid="save-category-btn"]').click();
    
    // Verify category was updated
    cy.get('[data-testid="category-name"]').first().should('contain', 'Work Projects');

    // Step 14: Check Profile
    cy.visit('/profile');
    cy.get('span').should('contain', 'John Doe');
    cy.get('span').should('contain', 'john@example.com');
    cy.get('.status').should('contain', 'Active');

    // Step 15: Logout
    cy.get('[data-testid="logout-btn"]').click();
    cy.url().should('include', '/auth/login');

    // Step 16: Login Again
    cy.get('[data-testid="email-input"]').type('john@example.com');
    cy.get('[data-testid="password-input"]').type('password123');
    cy.get('[data-testid="login-btn"]').click();
    
    // Should redirect to dashboard
    cy.url().should('include', '/dashboard');
    cy.get('h2').should('contain', 'Welcome to TaskFlow');

    // Step 17: Verify Data Persistence
    cy.visit('/tasks');
    cy.get('[data-testid="task-title"]').should('have.length', 2);
    cy.get('[data-testid="task-title"]').should('contain', 'Complete Project Proposal - Updated');
    cy.get('[data-testid="task-title"]').should('contain', 'Team Meeting');
    
    cy.visit('/categories');
    cy.get('[data-testid="category-name"]').should('have.length', 2);
    cy.get('[data-testid="category-name"]').should('contain', 'Work Projects');
    cy.get('[data-testid="category-name"]').should('contain', 'Personal');
  });

  it('should handle error scenarios gracefully', () => {
    // Register user
    cy.register('Test User', 'test@example.com', 'password123');
    
    // Test network error handling
    cy.intercept('GET', '/api/tasks*', { statusCode: 500 }).as('tasksError');
    cy.visit('/tasks');
    cy.wait('@tasksError');
    
    // Should show error state
    cy.get('.error-state').should('be.visible');
    cy.get('.btn-secondary').should('contain', 'Retry');
    
    // Test retry functionality
    cy.intercept('GET', '/api/tasks*', { fixture: 'tasks.json' }).as('tasksSuccess');
    cy.get('.btn-secondary').click();
    cy.wait('@tasksSuccess');
    
    // Error should be cleared
    cy.get('.error-state').should('not.exist');
  });

  it('should work on different screen sizes', () => {
    // Register user
    cy.register('Test User', 'test@example.com', 'password123');
    
    // Test mobile viewport
    cy.viewport(375, 667);
    cy.visit('/dashboard');
    cy.get('.stats-grid').should('be.visible');
    
    cy.visit('/tasks');
    cy.get('[data-testid="add-task-btn"]').should('be.visible');
    
    // Test tablet viewport
    cy.viewport(768, 1024);
    cy.visit('/dashboard');
    cy.get('.dashboard-content').should('be.visible');
    
    // Test desktop viewport
    cy.viewport(1280, 720);
    cy.visit('/dashboard');
    cy.get('.dashboard-content').should('be.visible');
  });
});
