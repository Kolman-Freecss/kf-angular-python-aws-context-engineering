import { HttpErrorResponse } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';

export interface AppError {
  id: string;
  message: string;
  details?: string;
  code?: string;
  timestamp: Date;
  context?: any;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: 'network' | 'validation' | 'authentication' | 'authorization' | 'server' | 'client';
  resolved: boolean;
}

export interface ErrorNotification {
  id: string;
  message: string;
  type: 'error' | 'warning' | 'info';
  duration?: number;
  action?: {
    label: string;
    callback: () => void;
  };
}

@Injectable({
  providedIn: 'root'
})
export class ErrorHandlerService {
  private router = inject(Router);
  
  // Error state management
  private errorsSubject = new BehaviorSubject<AppError[]>([]);
  private notificationsSubject = new BehaviorSubject<ErrorNotification[]>([]);
  
  // Signals for reactive state
  errors = signal<AppError[]>([]);
  notifications = signal<ErrorNotification[]>([]);
  isOnline = signal(navigator.onLine);
  
  // Error statistics
  private errorStats = signal({
    total: 0,
    byCategory: {} as Record<string, number>,
    bySeverity: {} as Record<string, number>,
    resolved: 0,
    unresolved: 0
  });

  constructor() {
    this.initializeErrorHandling();
    this.setupNetworkMonitoring();
  }

  /**
   * Initialize error handling
   */
  private initializeErrorHandling(): void {
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.handleError({
        message: event.reason?.message || 'Unhandled promise rejection',
        details: event.reason?.stack || event.reason,
        category: 'client',
        severity: 'high'
      });
    });

    // Handle global errors
    window.addEventListener('error', (event) => {
      this.handleError({
        message: event.message || 'Global error occurred',
        details: event.error?.stack,
        category: 'client',
        severity: 'high',
        context: {
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno
        }
      });
    });
  }

  /**
   * Setup network monitoring
   */
  private setupNetworkMonitoring(): void {
    window.addEventListener('online', () => {
      this.isOnline.set(true);
      this.showNotification({
        message: 'Connection restored',
        type: 'info',
        duration: 3000
      });
    });

    window.addEventListener('offline', () => {
      this.isOnline.set(false);
      this.handleError({
        message: 'Network connection lost',
        category: 'network',
        severity: 'medium'
      });
    });
  }

  /**
   * Handle HTTP errors
   */
  handleHttpError(error: HttpErrorResponse, context?: any): void {
    let appError: Partial<AppError>;

    switch (error.status) {
      case 400:
        appError = {
          message: 'Bad Request',
          details: error.error?.message || 'Invalid request data',
          code: 'BAD_REQUEST',
          category: 'validation',
          severity: 'medium'
        };
        break;

      case 401:
        appError = {
          message: 'Authentication Required',
          details: 'Please log in to continue',
          code: 'UNAUTHORIZED',
          category: 'authentication',
          severity: 'high'
        };
        // Redirect to login
        this.router.navigate(['/auth/login']);
        break;

      case 403:
        appError = {
          message: 'Access Denied',
          details: 'You do not have permission to perform this action',
          code: 'FORBIDDEN',
          category: 'authorization',
          severity: 'high'
        };
        break;

      case 404:
        appError = {
          message: 'Resource Not Found',
          details: 'The requested resource could not be found',
          code: 'NOT_FOUND',
          category: 'client',
          severity: 'medium'
        };
        break;

      case 409:
        appError = {
          message: 'Conflict',
          details: error.error?.message || 'Resource conflict occurred',
          code: 'CONFLICT',
          category: 'validation',
          severity: 'medium'
        };
        break;

      case 422:
        appError = {
          message: 'Validation Error',
          details: this.formatValidationErrors(error.error?.validation_errors),
          code: 'VALIDATION_ERROR',
          category: 'validation',
          severity: 'medium'
        };
        break;

      case 429:
        appError = {
          message: 'Rate Limit Exceeded',
          details: 'Too many requests. Please try again later.',
          code: 'RATE_LIMIT',
          category: 'server',
          severity: 'medium'
        };
        break;

      case 500:
        appError = {
          message: 'Server Error',
          details: 'An internal server error occurred',
          code: 'INTERNAL_ERROR',
          category: 'server',
          severity: 'high'
        };
        break;

      case 502:
      case 503:
      case 504:
        appError = {
          message: 'Service Unavailable',
          details: 'The service is temporarily unavailable',
          code: 'SERVICE_UNAVAILABLE',
          category: 'server',
          severity: 'high'
        };
        break;

      default:
        appError = {
          message: 'Unknown Error',
          details: error.message || 'An unexpected error occurred',
          code: 'UNKNOWN_ERROR',
          category: 'client',
          severity: 'medium'
        };
    }

    this.handleError({
      ...appError,
      context: {
        ...context,
        url: error.url,
        status: error.status,
        statusText: error.statusText
      }
    });
  }

  /**
   * Handle general application errors
   */
  handleError(error: Partial<AppError>): void {
    const appError: AppError = {
      id: this.generateErrorId(),
      message: error.message || 'Unknown error occurred',
      details: error.details,
      code: error.code,
      timestamp: new Date(),
      context: error.context,
      severity: error.severity || 'medium',
      category: error.category || 'client',
      resolved: false
    };

    // Add to errors list
    const currentErrors = this.errors();
    this.errors.set([appError, ...currentErrors]);
    this.errorsSubject.next([appError, ...currentErrors]);

    // Update statistics
    this.updateErrorStats(appError);

    // Show notification based on severity
    this.showErrorNotification(appError);

    // Log error
    this.logError(appError);
  }

  /**
   * Show error notification
   */
  private showErrorNotification(error: AppError): void {
    const notification: ErrorNotification = {
      id: this.generateErrorId(),
      message: error.message,
      type: this.getNotificationType(error.severity),
      duration: this.getNotificationDuration(error.severity),
      action: error.severity === 'critical' ? {
        label: 'Retry',
        callback: () => this.retryLastAction()
      } : undefined
    };

    this.addNotification(notification);
  }

  /**
   * Add notification
   */
  addNotification(notification: ErrorNotification): void {
    const currentNotifications = this.notifications();
    this.notifications.set([notification, ...currentNotifications]);
    this.notificationsSubject.next([notification, ...currentNotifications]);

    // Auto-remove notification after duration
    if (notification.duration) {
      setTimeout(() => {
        this.removeNotification(notification.id);
      }, notification.duration);
    }
  }

  /**
   * Remove notification
   */
  removeNotification(id: string): void {
    const currentNotifications = this.notifications();
    const filtered = currentNotifications.filter(n => n.id !== id);
    this.notifications.set(filtered);
    this.notificationsSubject.next(filtered);
  }

  /**
   * Clear all notifications
   */
  clearNotifications(): void {
    this.notifications.set([]);
    this.notificationsSubject.next([]);
  }

  /**
   * Mark error as resolved
   */
  resolveError(errorId: string): void {
    const currentErrors = this.errors();
    const updatedErrors = currentErrors.map(error => 
      error.id === errorId ? { ...error, resolved: true } : error
    );
    
    this.errors.set(updatedErrors);
    this.errorsSubject.next(updatedErrors);
    this.updateErrorStats();
  }

  /**
   * Clear resolved errors
   */
  clearResolvedErrors(): void {
    const currentErrors = this.errors();
    const unresolvedErrors = currentErrors.filter(error => !error.resolved);
    
    this.errors.set(unresolvedErrors);
    this.errorsSubject.next(unresolvedErrors);
    this.updateErrorStats();
  }

  /**
   * Clear all errors
   */
  clearAllErrors(): void {
    this.errors.set([]);
    this.errorsSubject.next([]);
    this.errorStats.set({
      total: 0,
      byCategory: {},
      bySeverity: {},
      resolved: 0,
      unresolved: 0
    });
  }

  /**
   * Get error statistics
   */
  getErrorStats() {
    return this.errorStats();
  }

  /**
   * Get errors observable
   */
  getErrorsObservable(): Observable<AppError[]> {
    return this.errorsSubject.asObservable();
  }

  /**
   * Get notifications observable
   */
  getNotificationsObservable(): Observable<ErrorNotification[]> {
    return this.notificationsSubject.asObservable();
  }

  /**
   * Format validation errors
   */
  private formatValidationErrors(validationErrors: any[]): string {
    if (!validationErrors || !Array.isArray(validationErrors)) {
      return 'Validation failed';
    }

    return validationErrors
      .map(error => `${error.loc?.join('.')}: ${error.msg}`)
      .join(', ');
  }

  /**
   * Generate unique error ID
   */
  private generateErrorId(): string {
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get notification type based on severity
   */
  private getNotificationType(severity: string): 'error' | 'warning' | 'info' {
    switch (severity) {
      case 'critical':
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      default:
        return 'info';
    }
  }

  /**
   * Get notification duration based on severity
   */
  private getNotificationDuration(severity: string): number {
    switch (severity) {
      case 'critical':
        return 0; // No auto-dismiss
      case 'high':
        return 10000; // 10 seconds
      case 'medium':
        return 5000; // 5 seconds
      default:
        return 3000; // 3 seconds
    }
  }

  /**
   * Update error statistics
   */
  private updateErrorStats(newError?: AppError): void {
    const currentStats = this.errorStats();
    const errors = this.errors();

    const stats = {
      total: errors.length,
      byCategory: {} as Record<string, number>,
      bySeverity: {} as Record<string, number>,
      resolved: errors.filter(e => e.resolved).length,
      unresolved: errors.filter(e => !e.resolved).length
    };

    // Count by category and severity
    errors.forEach(error => {
      stats.byCategory[error.category] = (stats.byCategory[error.category] || 0) + 1;
      stats.bySeverity[error.severity] = (stats.bySeverity[error.severity] || 0) + 1;
    });

    this.errorStats.set(stats);
  }

  /**
   * Log error to console or external service
   */
  private logError(error: AppError): void {
    const logData = {
      id: error.id,
      message: error.message,
      details: error.details,
      code: error.code,
      timestamp: error.timestamp.toISOString(),
      context: error.context,
      severity: error.severity,
      category: error.category,
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    // Log to console
    console.error('Application Error:', logData);

    // In production, you would send this to an error tracking service
    // Example: Sentry, LogRocket, etc.
    if (error.severity === 'critical' || error.severity === 'high') {
      // Send critical errors to external service
      this.sendErrorToExternalService(logData);
    }
  }

  /**
   * Send error to external service
   */
  private sendErrorToExternalService(errorData: any): void {
    // Implement external error reporting service integration
    // Example: Sentry, LogRocket, Bugsnag, etc.
    console.log('Sending error to external service:', errorData);
  }

  /**
   * Retry last action
   */
  private retryLastAction(): void {
    // Implement retry logic for critical errors
    window.location.reload();
  }

  /**
   * Show notification
   */
  showNotification(notification: Omit<ErrorNotification, 'id'>): void {
    const fullNotification: ErrorNotification = {
      ...notification,
      id: this.generateErrorId()
    };

    this.addNotification(fullNotification);
  }
}
