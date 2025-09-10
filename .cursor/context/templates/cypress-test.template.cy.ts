// Cypress E2E test template
describe('{{FeatureName}} E2E', () => {
  beforeEach(() => {
    // TODO: Set up API intercepts
    cy.intercept('GET', '/api/{{endpoint}}', { fixture: '{{endpoint}}.json' }).as('get{{Endpoint}}');
    cy.intercept('POST', '/api/{{endpoint}}', { statusCode: 201 }).as('create{{Endpoint}}');
    cy.intercept('PUT', '/api/{{endpoint}}/*', { statusCode: 200 }).as('update{{Endpoint}}');
    cy.intercept('DELETE', '/api/{{endpoint}}/*', { statusCode: 204 }).as('delete{{Endpoint}}');
    
    // TODO: Visit the appropriate page
    cy.visit('/{{page-route}}');
  });

  it('should display {{feature-name}} list', () => {
    cy.wait('@get{{Endpoint}}');
    
    // Use data-testid to select elements
    cy.get('[data-testid="{{feature-name}}-list"]').should('be.visible');
    cy.get('[data-testid="{{feature-name}}-item"]').should('have.length.greaterThan', 0);
  });

  it('should create new {{feature-name}}', () => {
    // Test behavior, not implementation
    cy.get('[data-testid="create-{{feature-name}}-button"]').click();
    
    // TODO: Fill form fields
    cy.get('[data-testid="{{field-name}}-input"]').type('{{test-value}}');
    
    cy.get('[data-testid="submit-{{feature-name}}-button"]').click();
    
    cy.wait('@create{{Endpoint}}');
    cy.get('[data-testid="success-message"]').should('contain', '{{SuccessMessage}}');
  });

  it('should handle loading states', () => {
    // Test loading states
    cy.get('[data-testid="loading"]').should('be.visible');
    cy.wait('@get{{Endpoint}}');
    cy.get('[data-testid="loading"]').should('not.exist');
  });

  it('should validate form inputs', () => {
    cy.get('[data-testid="create-{{feature-name}}-button"]').click();
    
    // Test validation
    cy.get('[data-testid="submit-{{feature-name}}-button"]').click();
    cy.get('[data-testid="error-message"]').should('contain', '{{RequiredField}}');
  });

  it('should update {{feature-name}}', () => {
    // TODO: Implement update test
    cy.get('[data-testid="edit-{{feature-name}}-button"]').first().click();
    
    // TODO: Update form fields
    cy.get('[data-testid="{{field-name}}-input"]').clear().type('{{updated-value}}');
    
    cy.get('[data-testid="submit-{{feature-name}}-button"]').click();
    
    cy.wait('@update{{Endpoint}}');
    cy.get('[data-testid="success-message"]').should('contain', '{{UpdateSuccessMessage}}');
  });

  it('should delete {{feature-name}}', () => {
    // TODO: Implement delete test
    cy.get('[data-testid="delete-{{feature-name}}-button"]').first().click();
    cy.get('[data-testid="confirm-delete-button"]').click();
    
    cy.wait('@delete{{Endpoint}}');
    cy.get('[data-testid="success-message"]').should('contain', '{{DeleteSuccessMessage}}');
  });
});
