import { HttpClient } from '@angular/common/http';
import { computed, Injectable, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface LoginRequest {
  username: string; // This should be the email
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly API_URL = 'http://localhost:8000/api/auth';
  private readonly TOKEN_KEY = 'taskflow_token';

  // Signals for reactive state management
  private _user = signal<User | null>(null);
  private _token = signal<string | null>(this.getStoredToken());

  // Computed values
  user = computed(() => this._user());
  isAuthenticated = computed(() => !!this._token());

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    // Initialize user from token if available
    if (this._token()) {
      this.loadUserProfile();
    }
  }

  login(credentials: LoginRequest): Observable<AuthResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    return this.http.post<AuthResponse>(`${this.API_URL}/token`, formData).pipe(
      tap(response => {
        this.setToken(response.access_token);
        this.loadUserProfile();
      })
    );
  }

  register(userData: RegisterRequest): Observable<User> {
    return this.http.post<User>(`${this.API_URL}/register`, userData);
  }

  logout(): void {
    this._token.set(null);
    this._user.set(null);
    localStorage.removeItem(this.TOKEN_KEY);
    this.router.navigate(['/auth/login']);
  }

  getToken(): string | null {
    return this._token();
  }

  getCurrentUser(): User | null {
    return this._user();
  }

  refreshToken(): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.API_URL}/refresh`, {}).pipe(
      tap(response => {
        this.setToken(response.access_token);
        this.loadUserProfile();
      })
    );
  }

  private setToken(token: string): void {
    this._token.set(token);
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  private getStoredToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  private loadUserProfile(): void {
    this.http.get<User>(`${this.API_URL}/me`).subscribe({
      next: (user) => this._user.set(user),
      error: () => this.logout()
    });
  }
}
