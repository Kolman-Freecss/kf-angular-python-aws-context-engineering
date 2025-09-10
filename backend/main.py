from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import engine, Base
from core.performance_middleware import PerformanceMiddleware
from core.error_handler import ErrorHandlerMiddleware
from core.monitoring import get_monitoring_service
from core.logging_config import setup_logging
from api import users, products, auth, tasks, files, notifications, analytics, websocket, advanced_tasks, cached_tasks
from models import user


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    Base.metadata.create_all(bind=engine)
    
    # Start monitoring
    monitoring_service = get_monitoring_service()
    await monitoring_service.start_monitoring(interval=60)
    
    yield
    
    # Shutdown
    await monitoring_service.stop_monitoring()


app = FastAPI(
    title="KF API",
    description="FastAPI backend with AWS integration",
    version="1.0.0",
    lifespan=lifespan
)

# Error handling middleware
app.add_middleware(ErrorHandlerMiddleware)

# Performance monitoring middleware
app.add_middleware(PerformanceMiddleware, slow_request_threshold=1.0)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(products.router, prefix="/api", tags=["products"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(files.router, prefix="/api", tags=["files"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(websocket.router, prefix="/api", tags=["websocket"])
app.include_router(advanced_tasks.router, prefix="/api/advanced", tags=["advanced-tasks"])
app.include_router(cached_tasks.router, prefix="/api/cached", tags=["cached-tasks"])


@app.get("/")
async def root():
    return {"message": "KF API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/performance/stats")
async def get_performance_stats():
    """Get performance statistics"""
    from core.performance_middleware import get_performance_middleware, get_db_performance_monitor
    
    middleware = get_performance_middleware()
    db_monitor = get_db_performance_monitor()
    
    return {
        "api_performance": middleware.get_performance_stats(),
        "database_performance": db_monitor.get_query_stats()
    }

@app.post("/performance/reset")
async def reset_performance_stats():
    """Reset performance statistics"""
    from core.performance_middleware import get_performance_middleware, get_db_performance_monitor
    
    middleware = get_performance_middleware()
    db_monitor = get_db_performance_monitor()
    
    middleware.reset_stats()
    db_monitor.reset_stats()
    
    return {"message": "Performance statistics reset successfully"}

@app.get("/monitoring/metrics")
async def get_monitoring_metrics():
    """Get current monitoring metrics"""
    monitoring_service = get_monitoring_service()
    return monitoring_service.get_current_metrics()

@app.get("/monitoring/alerts")
async def get_monitoring_alerts(unresolved_only: bool = True):
    """Get monitoring alerts"""
    monitoring_service = get_monitoring_service()
    return monitoring_service.get_alerts(unresolved_only=unresolved_only)

@app.post("/monitoring/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve a monitoring alert"""
    monitoring_service = get_monitoring_service()
    success = monitoring_service.resolve_alert(alert_id)
    
    if success:
        return {"message": f"Alert {alert_id} resolved successfully"}
    else:
        return {"message": f"Alert {alert_id} not found"}, 404

@app.get("/monitoring/health")
async def get_health_status():
    """Get overall health status"""
    monitoring_service = get_monitoring_service()
    return monitoring_service.get_health_status()

@app.post("/monitoring/thresholds")
async def update_monitoring_thresholds(thresholds: dict):
    """Update monitoring thresholds"""
    monitoring_service = get_monitoring_service()
    monitoring_service.update_thresholds(thresholds)
    return {"message": "Monitoring thresholds updated successfully"}
