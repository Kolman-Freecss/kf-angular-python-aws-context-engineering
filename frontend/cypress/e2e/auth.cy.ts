describe('Authentication Flow', () => {
  beforeEach(() => {
    // Clear any existing session
    cy.clearCookies();
    cy.clearLocalStorage();
  });

  describe('User Registration', () => {
    it('should register a new user successfully', () => {
      const userData = {
        fullName: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      };

      cy.visit('/auth/register');
      
      // Fill registration form
      cy.get('[data-testid="full-name-input"]').type(userData.fullName);
      cy.get('[data-testid="email-input"]').type(userData.email);
      cy.get('[data-testid="password-input"]').type(userData.password);
      cy.get('[data-testid="confirm-password-input"]').type(userData.password);
      
      // Submit form
      cy.get('[data-testid="register-btn"]').click();
      
      // Should redirect to dashboard
      cy.url().should('include', '/dashboard');
      cy.get('h2').should('contain', 'Welcome to TaskFlow');
    });

    it('should show validation errors for invalid registration data', () => {
      cy.visit('/auth/register');
      
      // Try to submit empty form
      cy.get('[data-testid="register-btn"]').click();
      
      // Should show validation errors
      cy.get('.error-message').should('be.visible');
    });

    it('should show error for password mismatch', () => {
      cy.visit('/auth/register');
      
      cy.get('[data-testid="full-name-input"]').type('Test User');
      cy.get('[data-testid="email-input"]').type('test@example.com');
      cy.get('[data-testid="password-input"]').type('password123');
      cy.get('[data-testid="confirm-password-input"]').type('differentpassword');
      
      cy.get('[data-testid="register-btn"]').click();
      
      // Should show password mismatch error
      cy.get('.error-message').should('contain', 'Passwords do not match');
    });
  });

  describe('User Login', () => {
    beforeEach(() => {
      // Register a user first
      cy.register('Test User', 'test@example.com', 'password123');
      cy.clearCookies();
      cy.clearLocalStorage();
    });

    it('should login with valid credentials', () => {
      cy.visit('/auth/login');
      
      cy.get('[data-testid="email-input"]').type('test@example.com');
      cy.get('[data-testid="password-input"]').type('password123');
      cy.get('[data-testid="login-btn"]').click();
      
      // Should redirect to dashboard
      cy.url().should('include', '/dashboard');
      cy.get('h2').should('contain', 'Welcome to TaskFlow');
    });

    it('should show error for invalid credentials', () => {
      cy.visit('/auth/login');
      
      cy.get('[data-testid="email-input"]').type('test@example.com');
      cy.get('[data-testid="password-input"]').type('wrongpassword');
      cy.get('[data-testid="login-btn"]').click();
      
      // Should show error message
      cy.get('.error-message').should('be.visible');
    });

    it('should show error for non-existent user', () => {
      cy.visit('/auth/login');
      
      cy.get('[data-testid="email-input"]').type('nonexistent@example.com');
      cy.get('[data-testid="password-input"]').type('password123');
      cy.get('[data-testid="login-btn"]').click();
      
      // Should show error message
      cy.get('.error-message').should('be.visible');
    });
  });

  describe('Protected Routes', () => {
    it('should redirect to login when accessing protected route without authentication', () => {
      cy.visit('/dashboard');
      cy.url().should('include', '/auth/login');
      
      cy.visit('/tasks');
      cy.url().should('include', '/auth/login');
      
      cy.visit('/categories');
      cy.url().should('include', '/auth/login');
    });

    it('should allow access to protected routes when authenticated', () => {
      cy.register('Test User', 'test@example.com', 'password123');
      
      cy.visit('/dashboard');
      cy.url().should('include', '/dashboard');
      
      cy.visit('/tasks');
      cy.url().should('include', '/tasks');
      
      cy.visit('/categories');
      cy.url().should('include', '/categories');
    });
  });

  describe('Navigation', () => {
    beforeEach(() => {
      cy.register('Test User', 'test@example.com', 'password123');
    });

    it('should navigate between pages using navigation menu', () => {
      // Test navigation from dashboard
      cy.visit('/dashboard');
      cy.get('nav a[href="/tasks"]').click();
      cy.url().should('include', '/tasks');
      
      cy.get('nav a[href="/categories"]').click();
      cy.url().should('include', '/categories');
      
      cy.get('nav a[href="/profile"]').click();
      cy.url().should('include', '/profile');
      
      cy.get('nav a[href="/dashboard"]').click();
      cy.url().should('include', '/dashboard');
    });

    it('should highlight active navigation item', () => {
      cy.visit('/tasks');
      cy.get('nav a[href="/tasks"]').should('have.class', 'active');
      
      cy.visit('/categories');
      cy.get('nav a[href="/categories"]').should('have.class', 'active');
    });
  });

  describe('Logout', () => {
    beforeEach(() => {
      cy.register('Test User', 'test@example.com', 'password123');
    });

    it('should logout and redirect to login page', () => {
      cy.visit('/profile');
      cy.get('[data-testid="logout-btn"]').click();
      
      cy.url().should('include', '/auth/login');
    });
  });
});
