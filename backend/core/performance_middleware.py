import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import psutil
import os

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor API performance and resource usage"""
    
    def __init__(self, app, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        self.request_count = 0
        self.total_response_time = 0.0
        self.slow_requests = 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timing
        start_time = time.time()
        
        # Get memory usage before request
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Increment request count
        self.request_count += 1
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error and re-raise
            logger.error(f"Request error: {request.url} - {str(e)}")
            raise
        
        # Calculate response time
        end_time = time.time()
        response_time = end_time - start_time
        
        # Get memory usage after request
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = memory_after - memory_before
        
        # Update statistics
        self.total_response_time += response_time
        if response_time > self.slow_request_threshold:
            self.slow_requests += 1
        
        # Log performance metrics
        self.log_performance_metrics(
            request=request,
            response=response,
            response_time=response_time,
            memory_delta=memory_delta
        )
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{response_time:.4f}s"
        response.headers["X-Memory-Delta"] = f"{memory_delta:.2f}MB"
        
        return response
    
    def log_performance_metrics(
        self,
        request: Request,
        response: Response,
        response_time: float,
        memory_delta: float
    ):
        """Log detailed performance metrics"""
        
        # Determine log level based on response time
        if response_time > self.slow_request_threshold:
            log_level = logging.WARNING
            log_message = "SLOW REQUEST"
        elif response.status_code >= 400:
            log_level = logging.ERROR
            log_message = "ERROR REQUEST"
        else:
            log_level = logging.INFO
            log_message = "REQUEST"
        
        # Log performance data
        logger.log(
            log_level,
            f"{log_message}: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {response_time:.4f}s - "
            f"Memory: {memory_delta:+.2f}MB - "
            f"User-Agent: {request.headers.get('user-agent', 'Unknown')[:50]}"
        )
        
        # Log slow requests with more detail
        if response_time > self.slow_request_threshold:
            logger.warning(
                f"SLOW REQUEST DETAILS: {request.method} {request.url} - "
                f"Query params: {dict(request.query_params)} - "
                f"Response time: {response_time:.4f}s - "
                f"Memory delta: {memory_delta:+.2f}MB"
            )
    
    def get_performance_stats(self) -> dict:
        """Get current performance statistics"""
        
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0
        )
        
        slow_request_percentage = (
            (self.slow_requests / self.request_count * 100) 
            if self.request_count > 0 else 0
        )
        
        # Get current system metrics
        process = psutil.Process(os.getpid())
        system_cpu = psutil.cpu_percent()
        system_memory = psutil.virtual_memory()
        
        return {
            'request_count': self.request_count,
            'total_response_time': round(self.total_response_time, 4),
            'average_response_time': round(avg_response_time, 4),
            'slow_requests': self.slow_requests,
            'slow_request_percentage': round(slow_request_percentage, 2),
            'process_memory_mb': round(process.memory_info().rss / 1024 / 1024, 2),
            'process_cpu_percent': round(process.cpu_percent(), 2),
            'system_cpu_percent': round(system_cpu, 2),
            'system_memory_percent': round(system_memory.percent, 2),
            'system_memory_available_gb': round(system_memory.available / 1024 / 1024 / 1024, 2)
        }
    
    def reset_stats(self):
        """Reset performance statistics"""
        self.request_count = 0
        self.total_response_time = 0.0
        self.slow_requests = 0
        logger.info("Performance statistics reset")

class DatabasePerformanceMonitor:
    """Monitor database query performance"""
    
    def __init__(self):
        self.query_count = 0
        self.total_query_time = 0.0
        self.slow_queries = []
        self.query_threshold = 0.1  # 100ms threshold for slow queries
    
    def log_query(self, query: str, execution_time: float, params: dict = None):
        """Log database query performance"""
        
        self.query_count += 1
        self.total_query_time += execution_time
        
        if execution_time > self.query_threshold:
            slow_query = {
                'query': query[:200] + '...' if len(query) > 200 else query,
                'execution_time': execution_time,
                'params': params,
                'timestamp': time.time()
            }
            self.slow_queries.append(slow_query)
            
            # Keep only last 100 slow queries
            if len(self.slow_queries) > 100:
                self.slow_queries = self.slow_queries[-100:]
            
            logger.warning(
                f"SLOW QUERY ({execution_time:.4f}s): {query[:100]}... "
                f"Params: {params}"
            )
    
    def get_query_stats(self) -> dict:
        """Get database query statistics"""
        
        avg_query_time = (
            self.total_query_time / self.query_count 
            if self.query_count > 0 else 0
        )
        
        return {
            'total_queries': self.query_count,
            'total_query_time': round(self.total_query_time, 4),
            'average_query_time': round(avg_query_time, 4),
            'slow_queries_count': len(self.slow_queries),
            'recent_slow_queries': self.slow_queries[-10:]  # Last 10 slow queries
        }
    
    def reset_stats(self):
        """Reset query statistics"""
        self.query_count = 0
        self.total_query_time = 0.0
        self.slow_queries = []
        logger.info("Database query statistics reset")

# Global instances
performance_middleware = None
db_performance_monitor = DatabasePerformanceMonitor()

def get_performance_middleware(slow_request_threshold: float = 1.0) -> PerformanceMiddleware:
    """Get performance middleware instance"""
    global performance_middleware
    if performance_middleware is None:
        performance_middleware = PerformanceMiddleware(None, slow_request_threshold)
    return performance_middleware

def get_db_performance_monitor() -> DatabasePerformanceMonitor:
    """Get database performance monitor instance"""
    return db_performance_monitor
