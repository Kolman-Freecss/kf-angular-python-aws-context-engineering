// E2E test example with Cypress
describe('User Management E2E', () => {
  beforeEach(() => {
    // Intercept API calls
    cy.intercept('GET', '/api/users', { fixture: 'users.json' }).as('getUsers');
    cy.intercept('POST', '/api/users', { statusCode: 201 }).as('createUser');
    
    cy.visit('/users');
  });

  it('should display users list', () => {
    cy.wait('@getUsers');
    
    // Use data-testid to select elements
    cy.get('[data-testid="users-list"]').should('be.visible');
    cy.get('[data-testid="user-item"]').should('have.length.greaterThan', 0);
  });

  it('should create new user', () => {
    // Test behavior, not implementation
    cy.get('[data-testid="create-user-button"]').click();
    
    cy.get('[data-testid="user-name-input"]').type('Juan Pérez');
    cy.get('[data-testid="user-email-input"]').type('juan@example.com');
    
    cy.get('[data-testid="submit-user-button"]').click();
    
    cy.wait('@createUser');
    cy.get('[data-testid="success-message"]').should('contain', 'User created');
  });

  it('should handle loading states', () => {
    // Test loading states
    cy.get('[data-testid="loading"]').should('be.visible');
    cy.wait('@getUsers');
    cy.get('[data-testid="loading"]').should('not.exist');
  });

  it('should validate form inputs', () => {
    cy.get('[data-testid="create-user-button"]').click();
    
    // Test validation
    cy.get('[data-testid="submit-user-button"]').click();
    cy.get('[data-testid="error-message"]').should('contain', 'Email required');
  });
});
