/// <reference types="cypress" />

// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Custom command to login a user
       * @example cy.login('user@example.com', 'password')
       */
      login(email: string, password: string): Chainable<void>
      
      /**
       * Custom command to register a new user
       * @example cy.register('John Doe', 'user@example.com', 'password')
       */
      register(fullName: string, email: string, password: string): Chainable<void>
      
      /**
       * Custom command to create a task
       * @example cy.createTask('Task Title', 'Task Description')
       */
      createTask(title: string, description?: string): Chainable<void>
      
      /**
       * Custom command to create a category
       * @example cy.createCategory('Work', '#3498db')
       */
      createCategory(name: string, color?: string): Chainable<void>
      
      /**
       * Custom command to wait for API calls to complete
       * @example cy.waitForApi()
       */
      waitForApi(): Chainable<void>
    }
  }
}

// Login command
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.visit('/auth/login');
  cy.get('[data-testid="email-input"]').type(email);
  cy.get('[data-testid="password-input"]').type(password);
  cy.get('[data-testid="login-btn"]').click();
  cy.url().should('include', '/dashboard');
});

// Register command
Cypress.Commands.add('register', (fullName: string, email: string, password: string) => {
  cy.visit('/auth/register');
  cy.get('[data-testid="full-name-input"]').type(fullName);
  cy.get('[data-testid="email-input"]').type(email);
  cy.get('[data-testid="password-input"]').type(password);
  cy.get('[data-testid="confirm-password-input"]').type(password);
  cy.get('[data-testid="register-btn"]').click();
  cy.url().should('include', '/dashboard');
});

// Create task command
Cypress.Commands.add('createTask', (title: string, description?: string) => {
  cy.visit('/tasks');
  cy.get('[data-testid="add-task-btn"]').click();
  cy.get('[data-testid="task-title-input"]').type(title);
  if (description) {
    cy.get('[data-testid="task-description-input"]').type(description);
  }
  cy.get('[data-testid="create-task-btn"]').click();
  cy.get('[data-testid="task-title"]').should('contain', title);
});

// Create category command
Cypress.Commands.add('createCategory', (name: string, color?: string) => {
  cy.visit('/categories');
  cy.get('[data-testid="add-category-btn"]').click();
  cy.get('[data-testid="category-name-input"]').type(name);
  if (color) {
    cy.get('[data-testid="category-color-input"]').clear().type(color);
  }
  cy.get('[data-testid="create-category-btn"]').click();
  cy.get('[data-testid="category-name"]').should('contain', name);
});

// Wait for API calls command
Cypress.Commands.add('waitForApi', () => {
  cy.intercept('GET', '/api/**').as('apiCall');
  cy.wait('@apiCall', { timeout: 10000 });
});
