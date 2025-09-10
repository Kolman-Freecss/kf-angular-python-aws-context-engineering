describe('Task Management', () => {
  beforeEach(() => {
    cy.clearCookies();
    cy.clearLocalStorage();
    cy.register('Test User', 'test@example.com', 'password123');
  });

  describe('Task Creation', () => {
    it('should create a new task successfully', () => {
      cy.visit('/tasks');
      
      // Click add task button
      cy.get('[data-testid="add-task-btn"]').click();
      
      // Fill task form
      cy.get('[data-testid="task-title-input"]').type('Test Task');
      cy.get('[data-testid="task-description-input"]').type('This is a test task description');
      cy.get('[data-testid="task-status-select"]').select('todo');
      cy.get('[data-testid="task-priority-select"]').select('medium');
      
      // Submit form
      cy.get('[data-testid="create-task-btn"]').click();
      
      // Verify task was created
      cy.get('[data-testid="task-title"]').should('contain', 'Test Task');
      cy.get('[data-testid="task-description"]').should('contain', 'This is a test task description');
    });

    it('should show validation error for empty title', () => {
      cy.visit('/tasks');
      cy.get('[data-testid="add-task-btn"]').click();
      
      // Try to submit without title
      cy.get('[data-testid="create-task-btn"]').click();
      
      // Should show validation error
      cy.get('.error-message').should('contain', 'Title is required');
    });

    it('should cancel task creation', () => {
      cy.visit('/tasks');
      cy.get('[data-testid="add-task-btn"]').click();
      
      // Fill some data
      cy.get('[data-testid="task-title-input"]').type('Test Task');
      
      // Cancel creation
      cy.get('[data-testid="cancel-create-btn"]').click();
      
      // Form should be hidden
      cy.get('[data-testid="task-title-input"]').should('not.exist');
    });
  });

  describe('Task Management', () => {
    beforeEach(() => {
      // Create a test task
      cy.createTask('Test Task', 'Test Description');
    });

    it('should display task in the list', () => {
      cy.visit('/tasks');
      
      cy.get('[data-testid="task-title"]').should('contain', 'Test Task');
      cy.get('[data-testid="task-description"]').should('contain', 'Test Description');
    });

    it('should edit task successfully', () => {
      cy.visit('/tasks');
      
      // Click edit button
      cy.get('[data-testid="edit-task-btn"]').click();
      
      // Update task details
      cy.get('[data-testid="edit-title-input"]').clear().type('Updated Task Title');
      cy.get('[data-testid="edit-description-input"]').clear().type('Updated description');
      
      // Save changes
      cy.get('[data-testid="save-task-btn"]').click();
      
      // Verify changes
      cy.get('[data-testid="task-title"]').should('contain', 'Updated Task Title');
      cy.get('[data-testid="task-description"]').should('contain', 'Updated description');
    });

    it('should update task status', () => {
      cy.visit('/tasks');
      
      // Change status to in progress
      cy.get('[data-testid="task-status-select"]').select('in_progress');
      
      // Verify status change
      cy.get('[data-testid="task-status-select"]').should('have.value', 'in_progress');
    });

    it('should update task priority', () => {
      cy.visit('/tasks');
      
      // Change priority to high
      cy.get('[data-testid="task-priority-select"]').select('high');
      
      // Verify priority change
      cy.get('[data-testid="task-priority-select"]').should('have.value', 'high');
    });

    it('should delete task successfully', () => {
      cy.visit('/tasks');
      
      // Click delete button
      cy.get('[data-testid="delete-task-btn"]').click();
      
      // Confirm deletion
      cy.on('window:confirm', () => true);
      
      // Verify task is removed
      cy.get('[data-testid="task-title"]').should('not.exist');
    });
  });

  describe('Task Filtering', () => {
    beforeEach(() => {
      // Create multiple tasks with different statuses
      cy.createTask('Todo Task', 'A task to do');
      cy.createTask('In Progress Task', 'A task in progress');
      
      // Update one task to in progress
      cy.visit('/tasks');
      cy.get('[data-testid="task-status-select"]').first().select('in_progress');
    });

    it('should filter tasks by status', () => {
      cy.visit('/tasks');
      
      // Filter by todo status
      cy.get('[data-testid="status-filter"]').select('todo');
      
      // Should only show todo tasks
      cy.get('[data-testid="task-title"]').should('have.length', 1);
      cy.get('[data-testid="task-title"]').should('contain', 'Todo Task');
    });

    it('should filter tasks by priority', () => {
      cy.visit('/tasks');
      
      // Set one task to high priority
      cy.get('[data-testid="task-priority-select"]').first().select('high');
      
      // Filter by high priority
      cy.get('[data-testid="priority-filter"]').select('high');
      
      // Should only show high priority tasks
      cy.get('[data-testid="task-title"]').should('have.length', 1);
    });

    it('should clear filters', () => {
      cy.visit('/tasks');
      
      // Apply filter
      cy.get('[data-testid="status-filter"]').select('todo');
      cy.get('[data-testid="task-title"]').should('have.length', 1);
      
      // Clear filters
      cy.get('[data-testid="clear-filters-btn"]').click();
      
      // Should show all tasks
      cy.get('[data-testid="task-title"]').should('have.length', 2);
    });
  });

  describe('Task Pagination', () => {
    beforeEach(() => {
      // Create multiple tasks to test pagination
      for (let i = 1; i <= 15; i++) {
        cy.createTask(`Task ${i}`, `Description for task ${i}`);
      }
    });

    it('should display pagination controls', () => {
      cy.visit('/tasks');
      
      cy.get('[data-testid="prev-page-btn"]').should('be.visible');
      cy.get('[data-testid="next-page-btn"]').should('be.visible');
      cy.get('.page-info').should('contain', 'Page 1');
    });

    it('should navigate to next page', () => {
      cy.visit('/tasks');
      
      cy.get('[data-testid="next-page-btn"]').click();
      cy.get('.page-info').should('contain', 'Page 2');
    });

    it('should navigate to previous page', () => {
      cy.visit('/tasks');
      
      // Go to page 2 first
      cy.get('[data-testid="next-page-btn"]').click();
      cy.get('.page-info').should('contain', 'Page 2');
      
      // Go back to page 1
      cy.get('[data-testid="prev-page-btn"]').click();
      cy.get('.page-info').should('contain', 'Page 1');
    });
  });

  describe('Empty State', () => {
    it('should show empty state when no tasks exist', () => {
      cy.visit('/tasks');
      
      cy.get('.empty-state').should('be.visible');
      cy.get('.empty-state').should('contain', 'No tasks found');
    });
  });

  describe('Loading States', () => {
    it('should show loading state while fetching tasks', () => {
      // Intercept API call to delay response
      cy.intercept('GET', '/api/tasks*', { delay: 1000 }).as('getTasks');
      
      cy.visit('/tasks');
      
      cy.get('.loading-state').should('be.visible');
      cy.get('.spinner').should('be.visible');
      
      cy.wait('@getTasks');
      cy.get('.loading-state').should('not.exist');
    });
  });
});
