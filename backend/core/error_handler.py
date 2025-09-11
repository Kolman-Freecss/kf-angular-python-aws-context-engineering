from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import logging
import traceback
from datetime import datetime
from typing import Union
from core.logging_config import ErrorHandler
from core.config import settings

logger = logging.getLogger(__name__)

class CustomHTTPException(HTTPException):
    """Custom HTTP exception with additional context"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        context: dict = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.context = context or {}

class ErrorHandlerMiddleware:
    """Centralized error handling middleware"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            await self.handle_exception(request, exc, send, scope, receive)
    
    async def handle_exception(self, request: Request, exc: Exception, send, scope, receive):
        """Handle different types of exceptions"""
        
        # Log the error
        self.log_error(request, exc)
        
        # Determine response based on exception type
        if isinstance(exc, CustomHTTPException):
            response = self.create_error_response(
                status_code=exc.status_code,
                message=exc.detail,
                error_code=exc.error_code,
                context=exc.context
            )
        elif isinstance(exc, HTTPException):
            response = self.create_error_response(
                status_code=exc.status_code,
                message=exc.detail
            )
        elif isinstance(exc, RequestValidationError):
            response = self.create_validation_error_response(exc)
        elif isinstance(exc, SQLAlchemyError):
            response = self.create_database_error_response(exc)
        elif isinstance(exc, ValidationError):
            response = self.create_validation_error_response(exc)
        else:
            response = self.create_generic_error_response(exc)
        
        # Send response
        await response(scope, receive, send)
    
    def log_error(self, request: Request, exc: Exception):
        """Log error with request context"""
        
        error_context = {
            'method': request.method,
            'url': str(request.url),
            'headers': dict(request.headers),
            'query_params': dict(request.query_params),
            'path_params': dict(request.path_params),
            'client_ip': request.client.host if request.client else None,
            'user_agent': request.headers.get('user-agent'),
            'correlation_id': getattr(request.state, 'correlation_id', None)
        }
        
        ErrorHandler.log_error(exc, error_context)
    
    def create_error_response(
        self,
        status_code: int,
        message: str,
        error_code: str = None,
        context: dict = None
    ) -> JSONResponse:
        """Create standardized error response"""
        
        response_data = {
            'error': True,
            'status_code': status_code,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if error_code:
            response_data['error_code'] = error_code
        
        if context:
            response_data['context'] = context
        
        # Include stack trace in development
        if settings.DEBUG:
            response_data['stack_trace'] = traceback.format_exc()
        
        return JSONResponse(
            status_code=status_code,
            content=response_data
        )
    
    def create_validation_error_response(self, exc: Union[RequestValidationError, ValidationError]) -> JSONResponse:
        """Create validation error response"""
        
        if isinstance(exc, RequestValidationError):
            errors = exc.errors()
            message = "Validation error"
        else:
            errors = exc.errors()
            message = "Data validation error"
        
        response_data = {
            'error': True,
            'status_code': 422,
            'message': message,
            'validation_errors': errors,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return JSONResponse(status_code=422, content=response_data)
    
    def create_database_error_response(self, exc: SQLAlchemyError) -> JSONResponse:
        """Create database error response"""
        
        if isinstance(exc, IntegrityError):
            status_code = 409  # Conflict
            message = "Database integrity constraint violation"
            error_code = "INTEGRITY_ERROR"
        else:
            status_code = 500
            message = "Database error occurred"
            error_code = "DATABASE_ERROR"
        
        response_data = {
            'error': True,
            'status_code': status_code,
            'message': message,
            'error_code': error_code,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Include error details in development
        if settings.DEBUG:
            response_data['details'] = str(exc)
        
        return JSONResponse(status_code=status_code, content=response_data)
    
    def create_generic_error_response(self, exc: Exception) -> JSONResponse:
        """Create generic error response"""
        
        response_data = {
            'error': True,
            'status_code': 500,
            'message': 'Internal server error',
            'error_code': 'INTERNAL_ERROR',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Include error details in development
        if settings.DEBUG:
            response_data['details'] = str(exc)
            response_data['stack_trace'] = traceback.format_exc()
        
        return JSONResponse(status_code=500, content=response_data)

# Exception classes for common errors
class AuthenticationError(CustomHTTPException):
    """Authentication related errors"""
    
    def __init__(self, message: str = "Authentication failed", context: dict = None):
        super().__init__(
            status_code=401,
            detail=message,
            error_code="AUTHENTICATION_ERROR",
            context=context
        )

class AuthorizationError(CustomHTTPException):
    """Authorization related errors"""
    
    def __init__(self, message: str = "Access denied", context: dict = None):
        super().__init__(
            status_code=403,
            detail=message,
            error_code="AUTHORIZATION_ERROR",
            context=context
        )

class ResourceNotFoundError(CustomHTTPException):
    """Resource not found errors"""
    
    def __init__(self, resource: str = "Resource", context: dict = None):
        super().__init__(
            status_code=404,
            detail=f"{resource} not found",
            error_code="RESOURCE_NOT_FOUND",
            context=context
        )

class ValidationError(CustomHTTPException):
    """Custom validation errors"""
    
    def __init__(self, message: str = "Validation failed", context: dict = None):
        super().__init__(
            status_code=422,
            detail=message,
            error_code="VALIDATION_ERROR",
            context=context
        )

class ConflictError(CustomHTTPException):
    """Conflict errors (e.g., duplicate resources)"""
    
    def __init__(self, message: str = "Resource conflict", context: dict = None):
        super().__init__(
            status_code=409,
            detail=message,
            error_code="CONFLICT_ERROR",
            context=context
        )

class RateLimitError(CustomHTTPException):
    """Rate limiting errors"""
    
    def __init__(self, message: str = "Rate limit exceeded", context: dict = None):
        super().__init__(
            status_code=429,
            detail=message,
            error_code="RATE_LIMIT_ERROR",
            context=context
        )

class ExternalServiceError(CustomHTTPException):
    """External service errors"""
    
    def __init__(self, service: str, message: str = "External service error", context: dict = None):
        super().__init__(
            status_code=502,
            detail=f"{service}: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            context=context
        )

# Utility functions for error handling
def handle_database_error(exc: SQLAlchemyError, context: str = None) -> CustomHTTPException:
    """Convert database errors to custom exceptions"""
    
    if isinstance(exc, IntegrityError):
        return ConflictError(
            message="Database integrity constraint violation",
            context={'operation': context, 'details': str(exc)}
        )
    else:
        return CustomHTTPException(
            status_code=500,
            detail="Database operation failed",
            error_code="DATABASE_ERROR",
            context={'operation': context, 'details': str(exc)}
        )

def handle_validation_error(exc: ValidationError, context: str = None) -> CustomHTTPException:
    """Convert validation errors to custom exceptions"""
    
    return ValidationError(
        message="Data validation failed",
        context={'operation': context, 'errors': exc.errors()}
    )

def handle_external_service_error(service: str, exc: Exception, context: str = None) -> CustomHTTPException:
    """Convert external service errors to custom exceptions"""
    
    return ExternalServiceError(
        service=service,
        message=str(exc),
        context={'operation': context}
    )

# Error response templates
ERROR_RESPONSES = {
    400: {
        'description': 'Bad Request',
        'content': {
            'application/json': {
                'example': {
                    'error': True,
                    'status_code': 400,
                    'message': 'Bad request',
                    'timestamp': '2024-01-01T00:00:00Z'
                }
            }
        }
    },
    401: {
        'description': 'Unauthorized',
        'content': {
            'application/json': {
                'example': {
                    'error': True,
                    'status_code': 401,
                    'message': 'Authentication failed',
                    'error_code': 'AUTHENTICATION_ERROR',
                    'timestamp': '2024-01-01T00:00:00Z'
                }
            }
        }
    },
    403: {
        'description': 'Forbidden',
        'content': {
            'application/json': {
                'example': {
                    'error': True,
                    'status_code': 403,
                    'message': 'Access denied',
                    'error_code': 'AUTHORIZATION_ERROR',
                    'timestamp': '2024-01-01T00:00:00Z'
                }
            }
        }
    },
    404: {
        'description': 'Not Found',
        'content': {
            'application/json': {
                'example': {
                    'error': True,
                    'status_code': 404,
                    'message': 'Resource not found',
                    'error_code': 'RESOURCE_NOT_FOUND',
                    'timestamp': '2024-01-01T00:00:00Z'
                }
            }
        }
    },
    409: {
        'description': 'Conflict',
        'content': {
            'application/json': {
                'example': {
                    'error': True,
                    'status_code': 409,
                    'message': 'Resource conflict',
                    'error_code': 'CONFLICT_ERROR',
                    'timestamp': '2024-01-01T00:00:00Z'
                }
            }
        }
    },
    422: {
        'description': 'Validation Error',
        'content': {
            'application/json': {
                'example': {
                    'error': True,
                    'status_code': 422,
                    'message': 'Validation failed',
                    'error_code': 'VALIDATION_ERROR',
                    'validation_errors': [],
                    'timestamp': '2024-01-01T00:00:00Z'
                }
            }
        }
    },
    429: {
        'description': 'Rate Limit Exceeded',
        'content': {
            'application/json': {
                'example': {
                    'error': True,
                    'status_code': 429,
                    'message': 'Rate limit exceeded',
                    'error_code': 'RATE_LIMIT_ERROR',
                    'timestamp': '2024-01-01T00:00:00Z'
                }
            }
        }
    },
    500: {
        'description': 'Internal Server Error',
        'content': {
            'application/json': {
                'example': {
                    'error': True,
                    'status_code': 500,
                    'message': 'Internal server error',
                    'error_code': 'INTERNAL_ERROR',
                    'timestamp': '2024-01-01T00:00:00Z'
                }
            }
        }
    },
    502: {
        'description': 'Bad Gateway',
        'content': {
            'application/json': {
                'example': {
                    'error': True,
                    'status_code': 502,
                    'message': 'External service error',
                    'error_code': 'EXTERNAL_SERVICE_ERROR',
                    'timestamp': '2024-01-01T00:00:00Z'
                }
            }
        }
    }
}
