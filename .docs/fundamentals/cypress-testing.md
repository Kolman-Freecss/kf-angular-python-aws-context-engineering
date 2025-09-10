# Cypress E2E Testing Fundamentals

## Core Concepts

### Test Structure
```typescript
describe('Feature Name', () => {
  beforeEach(() => {
    // Setup before each test
    cy.visit('/page');
  });

  it('should perform specific action', () => {
    // Test implementation
  });
});
```

### Element Selection
Use `data-testid` attributes for reliable element selection:

```typescript
// Good - using data-testid
cy.get('[data-testid="submit-button"]').click();

// Avoid - using CSS classes or IDs
cy.get('.btn-primary').click();
cy.get('#submit-btn').click();
```

### API Interception
Mock API calls for consistent testing:

```typescript
beforeEach(() => {
  cy.intercept('GET', '/api/users', { fixture: 'users.json' }).as('getUsers');
  cy.intercept('POST', '/api/users', { statusCode: 201 }).as('createUser');
});

it('should load users', () => {
  cy.wait('@getUsers');
  cy.get('[data-testid="users-list"]').should('be.visible');
});
```

## Testing Patterns

### Form Testing
```typescript
it('should submit form with valid data', () => {
  cy.get('[data-testid="name-input"]').type('John Doe');
  cy.get('[data-testid="email-input"]').type('john@example.com');
  cy.get('[data-testid="submit-button"]').click();
  
  cy.get('[data-testid="success-message"]').should('contain', 'User created');
});
```

### Loading State Testing
```typescript
it('should show loading state', () => {
  cy.get('[data-testid="loading"]').should('be.visible');
  cy.wait('@getUsers');
  cy.get('[data-testid="loading"]').should('not.exist');
});
```

### Error Handling Testing
```typescript
it('should display error message', () => {
  cy.intercept('POST', '/api/users', { statusCode: 400 }).as('createUserError');
  
  cy.get('[data-testid="submit-button"]').click();
  cy.wait('@createUserError');
  cy.get('[data-testid="error-message"]').should('contain', 'Error occurred');
});
```

### Navigation Testing
```typescript
it('should navigate between pages', () => {
  cy.get('[data-testid="users-link"]').click();
  cy.url().should('include', '/users');
  cy.get('[data-testid="users-page"]').should('be.visible');
});
```

## Best Practices

### Test Organization
```
cypress/e2e/
├── features/
│   ├── users/
│   │   ├── user-list.cy.ts
│   │   ├── user-form.cy.ts
│   │   └── user-details.cy.ts
│   └── products/
│       ├── product-list.cy.ts
│       └── product-form.cy.ts
├── fixtures/
│   ├── users.json
│   └── products.json
└── support/
    ├── commands.ts
    └── e2e.ts
```

### Custom Commands
```typescript
// cypress/support/commands.ts
declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>;
      createUser(userData: any): Chainable<void>;
    }
  }
}

Cypress.Commands.add('login', (email: string, password: string) => {
  cy.get('[data-testid="email-input"]').type(email);
  cy.get('[data-testid="password-input"]').type(password);
  cy.get('[data-testid="login-button"]').click();
});

Cypress.Commands.add('createUser', (userData: any) => {
  cy.get('[data-testid="name-input"]').type(userData.name);
  cy.get('[data-testid="email-input"]').type(userData.email);
  cy.get('[data-testid="submit-button"]').click();
});
```

### Fixtures
```json
// cypress/fixtures/users.json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "isActive": true
  },
  {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane@example.com",
    "isActive": false
  }
]
```

### Configuration
```typescript
// cypress.config.ts
import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    supportFile: 'cypress/support/e2e.ts',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,
  },
});
```

## Testing Strategies

### Page Object Model
```typescript
// cypress/support/pages/UserPage.ts
export class UserPage {
  elements = {
    usersList: () => cy.get('[data-testid="users-list"]'),
    createButton: () => cy.get('[data-testid="create-user-button"]'),
    nameInput: () => cy.get('[data-testid="name-input"]'),
    emailInput: () => cy.get('[data-testid="email-input"]'),
    submitButton: () => cy.get('[data-testid="submit-button"]'),
    successMessage: () => cy.get('[data-testid="success-message"]'),
  };

  visit() {
    cy.visit('/users');
    return this;
  }

  createUser(name: string, email: string) {
    this.elements.createButton().click();
    this.elements.nameInput().type(name);
    this.elements.emailInput().type(email);
    this.elements.submitButton().click();
    return this;
  }

  shouldShowSuccessMessage(message: string) {
    this.elements.successMessage().should('contain', message);
    return this;
  }
}
```

### Test Data Management
```typescript
// cypress/support/test-data.ts
export const testUsers = {
  valid: {
    name: 'John Doe',
    email: 'john@example.com',
    password: 'securepassword123'
  },
  invalid: {
    name: '',
    email: 'invalid-email',
    password: '123'
  }
};
```

## Best Practices

1. **Use data-testid attributes** for element selection
2. **Test behavior, not implementation** - focus on user actions
3. **Mock external dependencies** with cy.intercept()
4. **Organize tests by feature** in separate folders
5. **Use custom commands** for reusable actions
6. **Keep tests independent** - each test should be able to run alone
7. **Use fixtures** for consistent test data
8. **Implement proper error handling** in tests
9. **Use page object model** for complex pages
10. **Write descriptive test names** that explain the expected behavior
