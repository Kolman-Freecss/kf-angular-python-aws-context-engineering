# Context Engineering Setup for Cursor

## Project Overview

**TaskFlow** - A comprehensive personal task management system designed to demonstrate and practice modern full-stack development with Angular 20, FastAPI, Cypress E2E testing, and AWS services integration.

## Context Engineering Structure

```
.cursor/
├── rules/                    # Technology-specific rules
│   ├── angular.mdc          # Angular 20 & NgRx patterns
│   ├── fastapi.mdc          # FastAPI & Pydantic patterns
│   ├── cypress.mdc          # E2E testing strategies
│   ├── docker.mdc           # Containerization best practices
│   ├── testing.mdc          # Testing strategies
│   └── aws.mdc              # AWS services integration
└── context/                 # Additional context
    ├── examples/            # Real-world code examples
    │   ├── angular-ngrx-example.ts
    │   ├── fastapi-router-example.py
    │   └── cypress-e2e-example.cy.ts
    ├── patterns/            # Architectural patterns
    │   ├── angular-architecture.md
    │   ├── fastapi-architecture.md
    │   ├── docker-architecture.md
    │   └── aws-localstack-setup.md
    └── templates/           # Code templates
        ├── angular-component.template.ts
        ├── fastapi-router.template.py
        └── cypress-test.template.cy.ts

.docs/                       # Project documentation
├── context/                 # Implementation context
│   ├── IMPLEMENTATION-GUIDE.md
│   ├── PRD-Phase1-Foundation.md
│   ├── PRD-Phase2-CoreFeatures.md
│   ├── PRD-Phase3-AdvancedFeatures.md
│   └── PRD-Phase4-TestingAndPolish.md
└── fundamentals/            # Technology fundamentals
    ├── Context-engineering-setup.md
    ├── angular-fundamentals.md
    ├── fastapi-fundamentals.md
    ├── cypress-testing.md
    └── docker-aws-setup.md
```

## Context Engineering Principles

### 1. Rule-Based Development
Each `.mdc` file contains specific rules that Cursor automatically applies:

- **Scope Definition**: Rules apply to specific file patterns using `globs`
- **Automatic Application**: Rules with `alwaysApply: true` are enforced automatically
- **Technology-Specific**: Each technology has its own rule set
- **Best Practices**: Rules enforce modern development patterns

### 2. Contextual Examples
Real-world code examples demonstrate:

- **Angular 20**: Standalone components, NgRx patterns, signals
- **FastAPI**: Router patterns, Pydantic models, dependency injection
- **Cypress**: E2E testing strategies, API mocking, user journey testing
- **Docker**: Multi-stage builds, security, optimization
- **AWS**: Service integration, LocalStack development

### 3. Architectural Patterns
Documented patterns provide:

- **Project Structure**: Consistent folder organization
- **Code Organization**: Feature-based architecture
- **Integration Patterns**: Service communication patterns
- **Testing Strategies**: Comprehensive testing approaches

### 4. Code Templates
Reusable templates for:

- **Component Creation**: Angular component templates
- **API Development**: FastAPI router templates
- **Test Writing**: Cypress test templates
- **Quick Start**: Rapid development patterns

## Implementation Workflow

### Phase 1: Foundation Setup
1. **Docker Infrastructure**: Multi-service containerization
2. **Angular 20 App**: Standalone components with routing
3. **FastAPI Backend**: JWT authentication and basic APIs
4. **Database Setup**: PostgreSQL with migrations
5. **E2E Testing**: Basic Cypress configuration

### Phase 2: Core Features
1. **Task Management**: Complete CRUD operations
2. **User Dashboard**: Analytics and task overview
3. **Categorization**: Task organization system
4. **File Upload**: S3 integration via LocalStack
5. **Comprehensive Testing**: E2E test coverage

### Phase 3: Advanced Features
1. **Email Notifications**: SES integration
2. **Background Processing**: Lambda functions
3. **Advanced Analytics**: Dashboard insights
4. **Real-time Features**: WebSocket integration
5. **AWS Services**: Full service integration

### Phase 4: Production Readiness
1. **Comprehensive Testing**: 95%+ coverage
2. **Performance Optimization**: Sub-2s load times
3. **Security Hardening**: Vulnerability assessment
4. **Production Deployment**: CI/CD pipeline
5. **Documentation**: Complete user guides

## Cursor Usage Guidelines

### 1. Rule Application
- Rules are automatically applied based on file patterns
- Each rule file defines specific coding standards
- Rules enforce modern development practices
- Technology-specific patterns are maintained

### 2. Context Utilization
- Use examples for reference when implementing features
- Follow patterns for consistent architecture
- Use templates for rapid development
- Reference documentation for best practices

### 3. Development Process
1. **Read PRD**: Understand feature requirements
2. **Check Rules**: Ensure compliance with coding standards
3. **Use Templates**: Start with provided templates
4. **Follow Patterns**: Maintain architectural consistency
5. **Test Thoroughly**: Use E2E testing strategies

## Success Metrics

### Code Quality
- **Type Safety**: 100% TypeScript coverage
- **Test Coverage**: >95% unit, >90% integration, >85% E2E
- **Performance**: <2s load times, <500KB bundle size
- **Security**: No critical vulnerabilities

### Development Efficiency
- **Rapid Prototyping**: Templates enable quick development
- **Consistent Patterns**: Rules ensure code consistency
- **Comprehensive Testing**: E2E tests catch integration issues
- **Documentation**: Clear guides for all technologies

### Learning Outcomes
- **Angular 20**: Mastery of standalone components and NgRx
- **FastAPI**: Proficiency in async APIs and Pydantic
- **Cypress**: Expertise in E2E testing strategies
- **AWS**: Understanding of cloud service integration
- **Docker**: Containerization and orchestration skills

## Maintenance and Updates

### Rule Updates
- Rules are updated based on technology evolution
- New patterns are added as they emerge
- Best practices are refined through experience
- Documentation is kept current

### Context Evolution
- Examples are updated with new patterns
- Templates are refined for better usability
- Patterns are documented as they mature
- Integration strategies are improved

This context engineering setup provides a comprehensive foundation for building modern, scalable applications while maintaining high code quality and development efficiency.
