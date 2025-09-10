from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import engine, Base
from api import users, products, auth, tasks, files, notifications, analytics, websocket, advanced_tasks
from models import user


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass


app = FastAPI(
    title="KF API",
    description="FastAPI backend with AWS integration",
    version="1.0.0",
    lifespan=lifespan
)

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


@app.get("/")
async def root():
    return {"message": "KF API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
