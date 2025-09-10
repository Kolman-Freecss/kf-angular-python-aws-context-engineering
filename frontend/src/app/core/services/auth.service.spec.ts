import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { AuthService } from './auth.service';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AuthService]
    });
    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  describe('login', () => {
    it('should login user successfully', () => {
      const loginData = { email: 'test@example.com', password: 'password123' };
      const mockResponse = {
        access_token: 'mock-token',
        token_type: 'bearer',
        user: { id: 1, email: 'test@example.com', full_name: 'Test User' }
      };

      service.login(loginData).subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(localStorage.getItem('token')).toBe('mock-token');
      });

      const req = httpMock.expectOne('/api/auth/login');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(loginData);
      req.flush(mockResponse);
    });

    it('should handle login error', () => {
      const loginData = { email: 'test@example.com', password: 'wrongpassword' };
      const mockError = { detail: 'Invalid credentials' };

      service.login(loginData).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error).toEqual(mockError);
        }
      });

      const req = httpMock.expectOne('/api/auth/login');
      req.flush(mockError, { status: 401, statusText: 'Unauthorized' });
    });
  });

  describe('register', () => {
    it('should register user successfully', () => {
      const registerData = {
        full_name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      };
      const mockResponse = {
        access_token: 'mock-token',
        token_type: 'bearer',
        user: { id: 1, email: 'test@example.com', full_name: 'Test User' }
      };

      service.register(registerData).subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(localStorage.getItem('token')).toBe('mock-token');
      });

      const req = httpMock.expectOne('/api/auth/register');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(registerData);
      req.flush(mockResponse);
    });

    it('should handle registration error', () => {
      const registerData = {
        full_name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      };
      const mockError = { detail: 'Email already exists' };

      service.register(registerData).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error).toEqual(mockError);
        }
      });

      const req = httpMock.expectOne('/api/auth/register');
      req.flush(mockError, { status: 400, statusText: 'Bad Request' });
    });
  });

  describe('logout', () => {
    it('should clear token and user data', () => {
      localStorage.setItem('token', 'mock-token');
      localStorage.setItem('user', JSON.stringify({ id: 1, email: 'test@example.com' }));

      service.logout();

      expect(localStorage.getItem('token')).toBeNull();
      expect(localStorage.getItem('user')).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when token exists', () => {
      localStorage.setItem('token', 'mock-token');
      expect(service.isAuthenticated()).toBe(true);
    });

    it('should return false when token does not exist', () => {
      localStorage.removeItem('token');
      expect(service.isAuthenticated()).toBe(false);
    });
  });

  describe('getCurrentUser', () => {
    it('should return current user from localStorage', () => {
      const mockUser = { id: 1, email: 'test@example.com', full_name: 'Test User' };
      localStorage.setItem('user', JSON.stringify(mockUser));

      expect(service.getCurrentUser()).toEqual(mockUser);
    });

    it('should return null when no user in localStorage', () => {
      localStorage.removeItem('user');
      expect(service.getCurrentUser()).toBeNull();
    });
  });

  describe('refreshToken', () => {
    it('should refresh token successfully', () => {
      const mockResponse = {
        access_token: 'new-token',
        token_type: 'bearer'
      };

      service.refreshToken().subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(localStorage.getItem('token')).toBe('new-token');
      });

      const req = httpMock.expectOne('/api/auth/refresh');
      expect(req.request.method).toBe('POST');
      req.flush(mockResponse);
    });

    it('should handle refresh token error', () => {
      service.refreshToken().subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.status).toBe(401);
        }
      });

      const req = httpMock.expectOne('/api/auth/refresh');
      req.flush({}, { status: 401, statusText: 'Unauthorized' });
    });
  });
});
