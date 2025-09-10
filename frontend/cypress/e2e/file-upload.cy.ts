describe('File Upload', () => {
  beforeEach(() => {
    cy.clearCookies();
    cy.clearLocalStorage();
    cy.register('Test User', 'test@example.com', 'password123');
    cy.createTask('Test Task', 'Task for file upload testing');
  });

  describe('File Upload Interface', () => {
    it('should display file upload area', () => {
      cy.visit('/tasks');
      
      cy.get('.file-upload-area').should('be.visible');
      cy.get('h4').should('contain', 'Drop files here or click to browse');
      cy.get('[data-testid="browse-files-btn"]').should('be.visible');
    });

    it('should show supported file formats', () => {
      cy.visit('/tasks');
      
      cy.get('p').should('contain', 'Supported formats: Images, PDFs, Documents, Spreadsheets, Presentations, Archives');
      cy.get('.file-limit').should('contain', 'Maximum file size: 10MB');
    });
  });

  describe('File Selection', () => {
    it('should open file dialog when clicking browse button', () => {
      cy.visit('/tasks');
      
      // Create a test file
      const fileName = 'test-document.txt';
      const fileContent = 'This is a test file content';
      
      cy.get('[data-testid="file-input"]').selectFile({
        contents: Cypress.Buffer.from(fileContent),
        fileName: fileName,
        mimeType: 'text/plain'
      });
      
      // File should be selected (we can't directly test the file dialog)
      cy.get('[data-testid="file-input"]').should('have.value');
    });

    it('should handle drag and drop', () => {
      cy.visit('/tasks');
      
      const fileName = 'test-document.txt';
      const fileContent = 'This is a test file content';
      
      // Simulate drag and drop
      cy.get('.file-upload-area')
        .trigger('dragover')
        .should('have.class', 'drag-over');
      
      cy.get('.file-upload-area')
        .trigger('drop', {
          dataTransfer: {
            files: [new File([fileContent], fileName, { type: 'text/plain' })]
          }
        });
      
      cy.get('.file-upload-area').should('not.have.class', 'drag-over');
    });
  });

  describe('File Validation', () => {
    it('should reject files that are too large', () => {
      cy.visit('/tasks');
      
      // Create a large file (over 10MB)
      const largeContent = 'x'.repeat(11 * 1024 * 1024); // 11MB
      
      cy.get('[data-testid="file-input"]').selectFile({
        contents: Cypress.Buffer.from(largeContent),
        fileName: 'large-file.txt',
        mimeType: 'text/plain'
      });
      
      // Should show error message
      cy.get('.error-message').should('contain', 'File size exceeds maximum allowed size');
    });

    it('should reject unsupported file types', () => {
      cy.visit('/tasks');
      
      cy.get('[data-testid="file-input"]').selectFile({
        contents: Cypress.Buffer.from('test content'),
        fileName: 'test.exe',
        mimeType: 'application/x-executable'
      });
      
      // Should show error message
      cy.get('.error-message').should('contain', 'File type is not allowed');
    });

    it('should accept supported file types', () => {
      cy.visit('/tasks');
      
      const fileName = 'test-document.pdf';
      const fileContent = 'PDF content';
      
      cy.get('[data-testid="file-input"]').selectFile({
        contents: Cypress.Buffer.from(fileContent),
        fileName: fileName,
        mimeType: 'application/pdf'
      });
      
      // Should not show error message
      cy.get('.error-message').should('not.exist');
    });
  });

  describe('File Upload Process', () => {
    it('should show upload progress', () => {
      cy.visit('/tasks');
      
      const fileName = 'test-document.txt';
      const fileContent = 'This is a test file content';
      
      // Intercept upload request to simulate progress
      cy.intercept('POST', '/api/tasks/*/files', { delay: 2000 }).as('uploadFile');
      
      cy.get('[data-testid="file-input"]').selectFile({
        contents: Cypress.Buffer.from(fileContent),
        fileName: fileName,
        mimeType: 'text/plain'
      });
      
      // Should show upload progress
      cy.get('.upload-progress').should('be.visible');
      cy.get('.progress-bar').should('be.visible');
      cy.get('h4').should('contain', 'Uploading files...');
      
      cy.wait('@uploadFile');
    });

    it('should complete upload successfully', () => {
      cy.visit('/tasks');
      
      const fileName = 'test-document.txt';
      const fileContent = 'This is a test file content';
      
      cy.get('[data-testid="file-input"]').selectFile({
        contents: Cypress.Buffer.from(fileContent),
        fileName: fileName,
        mimeType: 'text/plain'
      });
      
      // Wait for upload to complete
      cy.get('.file-item', { timeout: 10000 }).should('be.visible');
      
      // Should show file in the list
      cy.get('.file-name').should('contain', fileName);
      cy.get('.file-meta').should('contain', 'Created:');
    });
  });

  describe('File Management', () => {
    beforeEach(() => {
      // Upload a test file
      cy.visit('/tasks');
      const fileName = 'test-document.txt';
      const fileContent = 'This is a test file content';
      
      cy.get('[data-testid="file-input"]').selectFile({
        contents: Cypress.Buffer.from(fileContent),
        fileName: fileName,
        mimeType: 'text/plain'
      });
      
      // Wait for upload to complete
      cy.get('.file-item', { timeout: 10000 }).should('be.visible');
    });

    it('should display file information correctly', () => {
      cy.get('.file-name').should('contain', 'test-document.txt');
      cy.get('.file-meta').should('contain', 'Created:');
      cy.get('.file-icon').should('contain', '📄'); // Text file icon
    });

    it('should download file when download button is clicked', () => {
      // Intercept download request
      cy.intercept('GET', '/api/files/*/download').as('downloadFile');
      
      cy.get('[data-testid="download-file-btn"]').click();
      
      cy.wait('@downloadFile');
    });

    it('should delete file when delete button is clicked', () => {
      cy.get('[data-testid="delete-file-btn"]').click();
      
      // Confirm deletion
      cy.on('window:confirm', () => true);
      
      // File should be removed from list
      cy.get('.file-item').should('not.exist');
    });

    it('should cancel file deletion', () => {
      cy.get('[data-testid="delete-file-btn"]').click();
      
      // Cancel deletion
      cy.on('window:confirm', () => false);
      
      // File should still be in list
      cy.get('.file-item').should('be.visible');
    });
  });

  describe('Multiple File Upload', () => {
    it('should upload multiple files', () => {
      cy.visit('/tasks');
      
      const files = [
        { name: 'file1.txt', content: 'Content 1', type: 'text/plain' },
        { name: 'file2.pdf', content: 'Content 2', type: 'application/pdf' },
        { name: 'file3.jpg', content: 'Content 3', type: 'image/jpeg' }
      ];
      
      files.forEach(file => {
        cy.get('[data-testid="file-input"]').selectFile({
          contents: Cypress.Buffer.from(file.content),
          fileName: file.name,
          mimeType: file.type
        });
      });
      
      // Should show all files in the list
      cy.get('.file-item', { timeout: 10000 }).should('have.length', 3);
    });
  });

  describe('File Types and Icons', () => {
    it('should display correct icons for different file types', () => {
      cy.visit('/tasks');
      
      const fileTypes = [
        { name: 'image.jpg', type: 'image/jpeg', expectedIcon: '🖼️' },
        { name: 'document.pdf', type: 'application/pdf', expectedIcon: '📄' },
        { name: 'spreadsheet.xlsx', type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', expectedIcon: '📊' },
        { name: 'archive.zip', type: 'application/zip', expectedIcon: '📦' }
      ];
      
      fileTypes.forEach(file => {
        cy.get('[data-testid="file-input"]').selectFile({
          contents: Cypress.Buffer.from('test content'),
          fileName: file.name,
          mimeType: file.type
        });
        
        // Wait for upload
        cy.get('.file-item', { timeout: 10000 }).should('be.visible');
        
        // Check icon
        cy.get('.file-icon').should('contain', file.expectedIcon);
      });
    });
  });

  describe('Error Handling', () => {
    it('should show error when upload fails', () => {
      cy.visit('/tasks');
      
      // Intercept upload request to return error
      cy.intercept('POST', '/api/tasks/*/files', { statusCode: 500 }).as('uploadError');
      
      const fileName = 'test-document.txt';
      const fileContent = 'This is a test file content';
      
      cy.get('[data-testid="file-input"]').selectFile({
        contents: Cypress.Buffer.from(fileContent),
        fileName: fileName,
        mimeType: 'text/plain'
      });
      
      cy.wait('@uploadError');
      
      // Should show error message
      cy.get('.error-message').should('contain', 'Failed to upload');
    });
  });

  describe('Empty State', () => {
    it('should show empty state when no files are uploaded', () => {
      cy.visit('/tasks');
      
      // Should not show file list initially
      cy.get('.file-list').should('not.exist');
    });
  });
});
