describe('Category Management', () => {
  beforeEach(() => {
    cy.clearCookies();
    cy.clearLocalStorage();
    cy.register('Test User', 'test@example.com', 'password123');
  });

  describe('Category Creation', () => {
    it('should create a new category successfully', () => {
      cy.visit('/categories');
      
      // Click add category button
      cy.get('[data-testid="add-category-btn"]').click();
      
      // Fill category form
      cy.get('[data-testid="category-name-input"]').type('Work');
      cy.get('[data-testid="category-color-input"]').clear().type('#3498db');
      
      // Submit form
      cy.get('[data-testid="create-category-btn"]').click();
      
      // Verify category was created
      cy.get('[data-testid="category-name"]').should('contain', 'Work');
      cy.get('.category-color').should('have.css', 'background-color', 'rgb(52, 152, 219)');
    });

    it('should show validation error for empty category name', () => {
      cy.visit('/categories');
      cy.get('[data-testid="add-category-btn"]').click();
      
      // Try to submit without name
      cy.get('[data-testid="create-category-btn"]').click();
      
      // Should show validation error
      cy.get('.error-message').should('contain', 'Category name is required');
    });

    it('should cancel category creation', () => {
      cy.visit('/categories');
      cy.get('[data-testid="add-category-btn"]').click();
      
      // Fill some data
      cy.get('[data-testid="category-name-input"]').type('Work');
      
      // Cancel creation
      cy.get('[data-testid="cancel-create-category-btn"]').click();
      
      // Form should be hidden
      cy.get('[data-testid="category-name-input"]').should('not.exist');
    });
  });

  describe('Category Management', () => {
    beforeEach(() => {
      // Create a test category
      cy.createCategory('Work', '#3498db');
    });

    it('should display category in the list', () => {
      cy.visit('/categories');
      
      cy.get('[data-testid="category-name"]').should('contain', 'Work');
      cy.get('.category-color').should('have.css', 'background-color', 'rgb(52, 152, 219)');
    });

    it('should edit category successfully', () => {
      cy.visit('/categories');
      
      // Click edit button
      cy.get('[data-testid="edit-category-btn"]').click();
      
      // Update category details
      cy.get('[data-testid="edit-category-name-input"]').clear().type('Updated Work');
      cy.get('[data-testid="edit-category-color-input"]').clear().type('#e74c3c');
      
      // Save changes
      cy.get('[data-testid="save-category-btn"]').click();
      
      // Verify changes
      cy.get('[data-testid="category-name"]').should('contain', 'Updated Work');
      cy.get('.category-color').should('have.css', 'background-color', 'rgb(231, 76, 60)');
    });

    it('should delete category successfully', () => {
      cy.visit('/categories');
      
      // Click delete button
      cy.get('[data-testid="delete-category-btn"]').click();
      
      // Confirm deletion
      cy.on('window:confirm', () => true);
      
      // Verify category is removed
      cy.get('[data-testid="category-name"]').should('not.exist');
    });

    it('should cancel category edit', () => {
      cy.visit('/categories');
      
      // Click edit button
      cy.get('[data-testid="edit-category-btn"]').click();
      
      // Make changes
      cy.get('[data-testid="edit-category-name-input"]').clear().type('Changed Name');
      
      // Cancel edit
      cy.get('[data-testid="cancel-edit-category-btn"]').click();
      
      // Verify original name is still there
      cy.get('[data-testid="category-name"]').should('contain', 'Work');
    });
  });

  describe('Category Usage in Tasks', () => {
    beforeEach(() => {
      // Create categories
      cy.createCategory('Work', '#3498db');
      cy.createCategory('Personal', '#e74c3c');
    });

    it('should assign category to task', () => {
      cy.visit('/tasks');
      
      // Create a task
      cy.get('[data-testid="add-task-btn"]').click();
      cy.get('[data-testid="task-title-input"]').type('Task with Category');
      cy.get('[data-testid="task-category-select"]').select('Work');
      cy.get('[data-testid="create-task-btn"]').click();
      
      // Verify category is assigned
      cy.get('[data-testid="task-category"]').should('contain', 'Work');
    });

    it('should filter tasks by category', () => {
      // Create tasks with different categories
      cy.visit('/tasks');
      cy.get('[data-testid="add-task-btn"]').click();
      cy.get('[data-testid="task-title-input"]').type('Work Task');
      cy.get('[data-testid="task-category-select"]').select('Work');
      cy.get('[data-testid="create-task-btn"]').click();
      
      cy.get('[data-testid="add-task-btn"]').click();
      cy.get('[data-testid="task-title-input"]').type('Personal Task');
      cy.get('[data-testid="task-category-select"]').select('Personal');
      cy.get('[data-testid="create-task-btn"]').click();
      
      // Filter by Work category
      cy.get('[data-testid="category-filter"]').select('Work');
      
      // Should only show Work tasks
      cy.get('[data-testid="task-title"]').should('have.length', 1);
      cy.get('[data-testid="task-title"]').should('contain', 'Work Task');
    });
  });

  describe('Category Deletion with Tasks', () => {
    beforeEach(() => {
      // Create category and task
      cy.createCategory('Work', '#3498db');
      cy.createTask('Work Task', 'A work task');
      
      // Assign category to task
      cy.visit('/tasks');
      cy.get('[data-testid="edit-task-btn"]').click();
      cy.get('[data-testid="edit-category-select"]').select('Work');
      cy.get('[data-testid="save-task-btn"]').click();
    });

    it('should prevent deletion of category with tasks', () => {
      cy.visit('/categories');
      
      // Try to delete category
      cy.get('[data-testid="delete-category-btn"]').click();
      cy.on('window:confirm', () => true);
      
      // Should show error message
      cy.get('.error-message').should('contain', 'Cannot delete category with tasks');
    });

    it('should allow deletion after removing tasks', () => {
      cy.visit('/tasks');
      
      // Remove category from task
      cy.get('[data-testid="edit-task-btn"]').click();
      cy.get('[data-testid="edit-category-select"]').select('');
      cy.get('[data-testid="save-task-btn"]').click();
      
      // Now delete category
      cy.visit('/categories');
      cy.get('[data-testid="delete-category-btn"]').click();
      cy.on('window:confirm', () => true);
      
      // Category should be deleted
      cy.get('[data-testid="category-name"]').should('not.exist');
    });
  });

  describe('Empty State', () => {
    it('should show empty state when no categories exist', () => {
      cy.visit('/categories');
      
      cy.get('.empty-state').should('be.visible');
      cy.get('.empty-state').should('contain', 'No categories yet');
    });
  });

  describe('Loading States', () => {
    it('should show loading state while fetching categories', () => {
      // Intercept API call to delay response
      cy.intercept('GET', '/api/categories*', { delay: 1000 }).as('getCategories');
      
      cy.visit('/categories');
      
      cy.get('.loading-state').should('be.visible');
      cy.get('.spinner').should('be.visible');
      
      cy.wait('@getCategories');
      cy.get('.loading-state').should('not.exist');
    });
  });
});
