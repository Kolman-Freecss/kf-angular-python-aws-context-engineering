import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { of, throwError } from 'rxjs';
import { AuthService } from '../../../core/services/auth.service';
import { LoginComponent } from './login.component';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
  let authService: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;

  beforeEach(async () => {
    const authServiceSpy = jasmine.createSpyObj('AuthService', ['login']);
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);

    await TestBed.configureTestingModule({
      imports: [ReactiveFormsModule],
      declarations: [LoginComponent],
      providers: [
        { provide: AuthService, useValue: authServiceSpy },
        { provide: Router, useValue: routerSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Form Validation', () => {
    it('should initialize with empty form', () => {
      expect(component.loginForm.value).toEqual({
        email: '',
        password: ''
      });
    });

    it('should validate email field', () => {
      const emailControl = component.loginForm.get('email');
      
      // Test required validation
      emailControl?.setValue('');
      expect(emailControl?.hasError('required')).toBe(true);
      
      // Test email format validation
      emailControl?.setValue('invalid-email');
      expect(emailControl?.hasError('email')).toBe(true);
      
      // Test valid email
      emailControl?.setValue('test@example.com');
      expect(emailControl?.valid).toBe(true);
    });

    it('should validate password field', () => {
      const passwordControl = component.loginForm.get('password');
      
      // Test required validation
      passwordControl?.setValue('');
      expect(passwordControl?.hasError('required')).toBe(true);
      
      // Test minimum length validation
      passwordControl?.setValue('123');
      expect(passwordControl?.hasError('minlength')).toBe(true);
      
      // Test valid password
      passwordControl?.setValue('password123');
      expect(passwordControl?.valid).toBe(true);
    });

    it('should disable submit button when form is invalid', () => {
      component.loginForm.patchValue({
        email: '',
        password: ''
      });
      fixture.detectChanges();
      
      const submitButton = fixture.debugElement.nativeElement.querySelector('button[type="submit"]');
      expect(submitButton.disabled).toBe(true);
    });

    it('should enable submit button when form is valid', () => {
      component.loginForm.patchValue({
        email: 'test@example.com',
        password: 'password123'
      });
      fixture.detectChanges();
      
      const submitButton = fixture.debugElement.nativeElement.querySelector('button[type="submit"]');
      expect(submitButton.disabled).toBe(false);
    });
  });

  describe('Form Submission', () => {
    beforeEach(() => {
      component.loginForm.patchValue({
        email: 'test@example.com',
        password: 'password123'
      });
    });

    it('should call authService.login with correct data on valid form submission', () => {
      const mockResponse = {
        access_token: 'mock-token',
        token_type: 'bearer',
        user: { 
          id: 1, 
          email: 'test@example.com', 
          full_name: 'Test User',
          is_active: true,
          created_at: '2023-01-01T00:00:00Z'
        }
      };
      authService.login.and.returnValue(of(mockResponse));

      component.onSubmit();

      expect(authService.login).toHaveBeenCalledWith({
        username: 'test@example.com',
        password: 'password123'
      });
    });

    it('should navigate to dashboard on successful login', () => {
      const mockResponse = {
        access_token: 'mock-token',
        token_type: 'bearer',
        user: { 
          id: 1, 
          email: 'test@example.com', 
          full_name: 'Test User',
          is_active: true,
          created_at: '2023-01-01T00:00:00Z'
        }
      };
      authService.login.and.returnValue(of(mockResponse));

      component.onSubmit();

      expect(router.navigate).toHaveBeenCalledWith(['/dashboard']);
    });

    it('should set loading state during login', () => {
      const mockResponse = {
        access_token: 'mock-token',
        token_type: 'bearer',
        user: { 
          id: 1, 
          email: 'test@example.com', 
          full_name: 'Test User',
          is_active: true,
          created_at: '2023-01-01T00:00:00Z'
        }
      };
      authService.login.and.returnValue(of(mockResponse));

      component.onSubmit();

      expect(component.isLoading()).toBe(true);
    });

    it('should handle login error', () => {
      const mockError = { detail: 'Invalid credentials' };
      authService.login.and.returnValue(throwError(() => mockError));

      component.onSubmit();

      expect(component.errorMessage()).toBe('Invalid email or password');
      expect(component.isLoading()).toBe(false);
    });

    it('should not submit form when invalid', () => {
      component.loginForm.patchValue({
        email: '',
        password: ''
      });

      component.onSubmit();

      expect(authService.login).not.toHaveBeenCalled();
    });
  });

  describe('Template Rendering', () => {
    it('should display error message when present', () => {
      component.errorMessage.set('Test error message');
      fixture.detectChanges();

      const errorElement = fixture.debugElement.nativeElement.querySelector('.error-message');
      expect(errorElement.textContent.trim()).toBe('Test error message');
    });

    it('should show loading state on button when loading', () => {
      component.isLoading.set(true);
      fixture.detectChanges();

      const submitButton = fixture.debugElement.nativeElement.querySelector('button[type="submit"]');
      expect(submitButton.textContent.trim()).toBe('Logging in...');
    });

    it('should show validation errors for touched invalid fields', () => {
      const emailControl = component.loginForm.get('email');
      emailControl?.setValue('');
      emailControl?.markAsTouched();
      fixture.detectChanges();

      const errorElement = fixture.debugElement.nativeElement.querySelector('.error-message');
      expect(errorElement.textContent.trim()).toBe('Please enter a valid email address');
    });

    it('should add error class to invalid touched input', () => {
      const emailControl = component.loginForm.get('email');
      emailControl?.setValue('');
      emailControl?.markAsTouched();
      fixture.detectChanges();

      const emailInput = fixture.debugElement.nativeElement.querySelector('input[formControlName="email"]');
      expect(emailInput.classList.contains('error')).toBe(true);
    });
  });

  describe('Accessibility', () => {
    it('should have proper form labels', () => {
      const emailLabel = fixture.debugElement.nativeElement.querySelector('label[for="email"]');
      const passwordLabel = fixture.debugElement.nativeElement.querySelector('label[for="password"]');
      
      expect(emailLabel.textContent.trim()).toBe('Email');
      expect(passwordLabel.textContent.trim()).toBe('Password');
    });

    it('should have proper input types', () => {
      const emailInput = fixture.debugElement.nativeElement.querySelector('input[type="email"]');
      const passwordInput = fixture.debugElement.nativeElement.querySelector('input[type="password"]');
      
      expect(emailInput).toBeTruthy();
      expect(passwordInput).toBeTruthy();
    });

    it('should have proper button type', () => {
      const submitButton = fixture.debugElement.nativeElement.querySelector('button[type="submit"]');
      expect(submitButton).toBeTruthy();
    });
  });
});
