# KF Angular-Python-AWS Context Engineering Project

A full-stack application demonstrating modern development practices with Angular 20, FastAPI, Cypress E2E testing, and AWS LocalStack integration.

## 🏗️ Architecture

- **Frontend**: Angular 20 with NgRx state management
- **Backend**: FastAPI with Pydantic models
- **Testing**: Cypress E2E tests
- **Containerization**: Docker with multi-stage builds
- **AWS**: LocalStack for local AWS service simulation

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- Python 3.11+
- Docker & Docker Compose

### Setup
```bash
# Clone and setup
git clone <repository-url>
cd kf-angular-python-aws-context-engineering

# Run setup script
./scripts/setup.sh
```

### Manual Setup
```bash
# Frontend
cd frontend
npm install
npm run build

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start services
docker-compose up -d
```

## 🌐 Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **LocalStack**: http://localhost:4566

## 📚 Documentation

### Context Engineering
- [Context Engineering Setup](.docs/fundamentals/Context-engineering-setup.md)
- [Angular Fundamentals](.docs/fundamentals/angular-fundamentals.md)
- [FastAPI Fundamentals](.docs/fundamentals/fastapi-fundamentals.md)
- [Cypress Testing](.docs/fundamentals/cypress-testing.md)
- [Docker & AWS Setup](.docs/fundamentals/docker-aws-setup.md)

### Cursor Rules
- [Angular Rules](.cursor/rules/angular.mdc)
- [FastAPI Rules](.cursor/rules/fastapi.mdc)
- [Cypress Rules](.cursor/rules/cypress.mdc)
- [Docker Rules](.cursor/rules/docker.mdc)

## 🧪 Testing

### E2E Tests
```bash
# Open Cypress
cd frontend
npm run e2e

# Run headless
npm run e2e:headless
```

### Unit Tests
```bash
# Frontend
cd frontend
npm test

# Backend
cd backend
source venv/bin/activate
pytest
```

## 🐳 Docker Commands

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Health check
./scripts/health-check.sh
```

## 🔧 Development

### Frontend Development
```bash
cd frontend
npm start  # Development server on http://localhost:4200
```

### Backend Development
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload  # API server on http://localhost:8000
```

## 📁 Project Structure

```
├── .cursor/                 # Context engineering rules
│   ├── rules/              # Technology-specific rules
│   └── context/            # Examples, patterns, templates
├── .docs/                  # Documentation
│   ├── context/            # Implementation context & PRDs
│   └── fundamentals/       # Technology fundamentals
├── frontend/               # Angular 20 application
│   ├── src/app/
│   │   ├── features/       # Feature modules
│   │   ├── shared/         # Shared components
│   │   └── core/           # Core services
│   └── cypress/            # E2E tests
├── backend/                # FastAPI application
│   ├── api/                # API routers
│   ├── core/               # Core functionality
│   ├── models/             # Pydantic models
│   ├── services/           # Business logic
│   └── schemas/            # Database schemas
├── scripts/                # Setup and utility scripts
└── docker-compose.yml      # Container orchestration
```

## 🎯 Context Engineering

This project uses Cursor's context engineering features:

1. **Rules (.mdc files)**: Automatic application of coding standards
2. **Examples**: Real-world code examples for each technology
3. **Patterns**: Architectural patterns and best practices
4. **Templates**: Code templates for rapid development

## 🔐 Environment Variables

Create `.env` files for configuration:

```bash
# .env.development
NODE_ENV=development
API_URL=http://localhost:8000
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
AWS_ENDPOINT=http://localhost:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
```

## 🤝 Contributing

1. Follow the established patterns in `.cursor/context/`
2. Use the provided templates for new components/features
3. Write E2E tests for all user-critical features
4. Follow the coding standards defined in `.cursor/rules/`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.