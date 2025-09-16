# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a full-stack application with Angular 20 frontend, FastAPI backend, and AWS LocalStack integration:

- **Frontend**: Angular 20 with NgRx state management, standalone components, signals, and Cypress E2E testing
- **Backend**: FastAPI with Pydantic models, SQLAlchemy async, JWT authentication, and comprehensive monitoring
- **Containerization**: Docker Compose orchestration with multi-stage builds
- **AWS Integration**: LocalStack for local AWS service simulation
- **Testing**: Comprehensive unit tests (Jasmine/Karma), E2E tests (Cypress), and backend tests (pytest)

## Essential Commands

### Frontend Development (run from `/frontend`)
```bash
npm start                 # Dev server at http://localhost:4200 (local development)
npm run start:docker      # Dev server with Docker backend services
npm run build            # Production build
npm run build:docker     # Build with Docker environment
npm test                 # Unit tests (headless)
npm run test:watch       # Unit tests (watch mode)
npm run test:coverage    # Unit tests with coverage
npm run e2e              # Open Cypress for E2E tests
npm run e2e:headless     # Run E2E tests headlessly
npm run lint             # ESLint
npm run lint:fix         # ESLint with auto-fix
npm run format           # Prettier formatting
npm run type-check       # TypeScript compilation check
```

### Backend Development (run from `/backend`)
```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Development
uvicorn main:app --reload  # API server at http://localhost:8000

# Testing
pytest                    # Run all tests
pytest -v                # Verbose output
pytest --cov            # With coverage
pytest tests/test_auth.py # Run specific test file
```

### Full Stack Development
```bash
# Docker Compose (from root)
docker-compose up -d --build  # Build and start all services
docker-compose logs -f        # View logs
docker-compose down           # Stop services

# Hybrid Development (Frontend local + Backend Docker)
docker-compose up -d db redis localstack backend celery celery-beat  # Start backend services only
cd frontend && npm run start:docker  # Run frontend locally with Docker backend

# Setup and development scripts
./scripts/setup.sh           # Complete project setup
./scripts/health-check.sh    # Verify all services
./scripts/dev-hybrid.sh      # Start hybrid development mode (Linux/Mac)
scripts/dev-hybrid.bat       # Start hybrid development mode (Windows)
```

## Key Development Patterns

### Frontend Architecture
- **Components**: Use standalone components exclusively with OnPush change detection
- **State**: NgRx for global state, signals for local state, computed() for derived state
- **DI**: Use `@inject()` instead of constructor injection, prefer functional guards
- **Forms**: Reactive forms only with typed form controls
- **Testing**: Use `data-testid` attributes, test behavior not implementation

### Backend Architecture
- **API Structure**: APIRouter per domain, proper HTTP status codes, async/await for I/O
- **Models**: Pydantic models with full typing, BaseModel inheritance patterns
- **Database**: SQLAlchemy async sessions, Alembic migrations, proper transaction management
- **Auth**: JWT tokens with OAuth2PasswordBearer, bcrypt password hashing
- **Error Handling**: HTTPException for API errors, proper logging throughout

### State Management
- **Frontend**: NgRx feature-based store structure with createAction/createReducer/createSelector patterns
- **Backend**: Dependency injection with Depends(), proper session management

### Testing Strategy
- **Frontend**: Jasmine/Karma for unit tests, Cypress for E2E, mock external dependencies
- **Backend**: pytest for unit/integration tests, fixtures for test data, test error scenarios

## Service URLs
- Frontend: http://localhost:3000 (production) / http://localhost:4200 (dev)
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- LocalStack AWS: http://localhost:4566

## Important Files and Directories

### Configuration
- `frontend/package.json` - Frontend dependencies and scripts
- `backend/requirements.txt` - Python dependencies
- `docker-compose.yml` - Container orchestration
- `.cursor/rules/` - Cursor IDE context engineering rules

### Key Architecture Files
- `backend/main.py` - FastAPI application entry point with middleware setup
- `backend/core/` - Core functionality (config, database, middleware, monitoring)
- `backend/api/` - API routers organized by domain
- `frontend/src/app/core/` - Core Angular services and guards
- `frontend/src/app/features/` - Feature modules with components

### Testing
- `backend/tests/` - Python test files using pytest
- `frontend/src/**/*.spec.ts` - Angular unit test files
- `frontend/cypress/` - E2E test specifications

## Context Engineering Rules

This project uses Cursor's context engineering with rules in `.cursor/rules/`:
- `angular.mdc` - Angular 20 best practices (standalone components, signals, NgRx patterns)
- `fastapi.mdc` - FastAPI patterns (async/await, Pydantic models, proper error handling)
- `general.mdc` - General development standards (typing, naming conventions)
- `testing.mdc` - Testing approaches and patterns
- `aws.mdc` - AWS integration patterns
- `docker.mdc` - Containerization best practices

## Performance & Monitoring

The backend includes comprehensive performance monitoring:
- Performance middleware tracking request times
- Database query monitoring
- Custom monitoring service with alerting
- Health check endpoints at `/health` and `/monitoring/health`
- Performance stats at `/performance/stats`

## Development Workflow

1. **Frontend Changes**: Use Angular standalone components, implement proper state management with NgRx
2. **Backend Changes**: Follow FastAPI async patterns, use proper Pydantic models
3. **Testing**: Write unit tests for all new functionality, add E2E tests for critical user flows
4. **Linting**: Always run `npm run lint` (frontend) before committing
5. **Type Checking**: Use `npm run type-check` (frontend) to verify TypeScript compilation

## Common Issues

- **CORS**: Configured in `backend/main.py` for frontend development
- **Database**: SQLite for development, configured in `backend/core/database.py`
- **Authentication**: JWT tokens implemented in `backend/api/auth.py`
- **File Uploads**: Handled in `backend/api/files.py` with S3 integration
- **WebSocket**: Real-time features in `backend/api/websocket.py`