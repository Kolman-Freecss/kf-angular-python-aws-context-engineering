import { HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { catchError, delay, retryWhen, take } from 'rxjs/operators';
import { ErrorHandlerService } from '../services/error-handler.service';

@Injectable()
export class GlobalErrorInterceptor implements HttpInterceptor {
  
  constructor(private errorHandler: ErrorHandlerService) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(request).pipe(
      retryWhen(errors => 
        errors.pipe(
          delay(1000),
          take(2) // Retry up to 2 times
        )
      ),
      catchError((error: HttpErrorResponse) => {
        // Handle different types of errors
        this.handleHttpError(error, request);
        
        // Re-throw the error for other interceptors or components to handle
        return throwError(() => error);
      })
    );
  }

  private handleHttpError(error: HttpErrorResponse, request: HttpRequest<any>): void {
    const context = {
      method: request.method,
      url: request.url,
      body: request.body,
      headers: request.headers.keys().reduce((acc, key) => {
        acc[key] = request.headers.get(key);
        return acc;
      }, {} as any)
    };

    // Handle specific error cases
    if (error.status === 0) {
      // Network error
      this.errorHandler.handleError({
        message: 'Network Error',
        details: 'Unable to connect to the server. Please check your internet connection.',
        category: 'network',
        severity: 'high',
        context
      });
    } else if (error.status >= 500) {
      // Server errors
      this.errorHandler.handleError({
        message: 'Server Error',
        details: `Server returned error ${error.status}: ${error.statusText}`,
        category: 'server',
        severity: 'high',
        context
      });
    } else if (error.status === 401) {
      // Authentication error
      this.errorHandler.handleError({
        message: 'Authentication Required',
        details: 'Your session has expired. Please log in again.',
        category: 'authentication',
        severity: 'high',
        context
      });
    } else if (error.status === 403) {
      // Authorization error
      this.errorHandler.handleError({
        message: 'Access Denied',
        details: 'You do not have permission to perform this action.',
        category: 'authorization',
        severity: 'high',
        context
      });
    } else if (error.status === 422) {
      // Validation error
      this.errorHandler.handleError({
        message: 'Validation Error',
        details: this.formatValidationErrors(error.error?.validation_errors),
        category: 'validation',
        severity: 'medium',
        context
      });
    } else {
      // Other client errors
      this.errorHandler.handleError({
        message: error.error?.message || 'Request Failed',
        details: `Error ${error.status}: ${error.statusText}`,
        category: 'client',
        severity: 'medium',
        context
      });
    }
  }

  private formatValidationErrors(validationErrors: any[]): string {
    if (!validationErrors || !Array.isArray(validationErrors)) {
      return 'Validation failed';
    }

    return validationErrors
      .map(error => `${error.loc?.join('.')}: ${error.msg}`)
      .join(', ');
  }
}
