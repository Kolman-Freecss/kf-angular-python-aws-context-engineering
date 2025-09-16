# KF Frontend

Angular 20 frontend application with modern architecture, state management, and comprehensive testing.

## Features

### 🔐 Authentication
- User registration and login
- JWT token-based authentication
- Protected routes with guards

### 📋 Task Management
- Create, read, update, delete tasks
- Task status tracking (todo, in-progress, done)
- Priority levels (low, medium, high, urgent)
- Due date management
- Task filtering and pagination

### 🏷️ Categories
- Create and manage task categories
- Color-coded category system
- Category assignment to tasks
- Category-based filtering

### 📊 Dashboard
- Task analytics and statistics
- Completion rate tracking
- Priority distribution charts
- Category-based task counts

### 📁 File Management
- File upload functionality
- AWS S3 integration
- File attachment to tasks

### 👤 User Profile
- Profile management
- User settings

## Architecture

### 🏗️ Core Technologies
- **Angular 20** with standalone components
  - Latest features and performance improvements
  - Tree-shakable imports and smaller bundles
  - Enhanced hydration and SSR support
  - Improved change detection algorithms
- **NgRx** for state management
  - Predictable state container
  - Time-travel debugging
  - Action replay and state inspection
  - Immutable state updates
- **Signals** for local reactive state
  - Fine-grained reactivity
  - Automatic dependency tracking
  - Better performance than Zone.js
  - Computed values with automatic updates
- **RxJS** for reactive programming
  - Powerful operators for data transformation
  - Async data handling
  - Error handling and retry logic
- **TypeScript** with strict typing
  - Type safety and better IDE support
  - Compile-time error detection
  - Enhanced refactoring capabilities

### 🔧 Development Patterns
- **Standalone Components** with OnPush change detection
  - No NgModules required
  - Better tree-shaking and smaller bundles
  - Simplified testing and development
- **Modern Dependency Injection** with `@inject()`
  - Functional approach to DI
  - Better type inference
  - Cleaner component constructors
- **Reactive Forms** with typed controls
  - Type-safe form handling
  - Built-in validation
  - Real-time form state management
- **Feature-based Routing** with lazy loading
  - Code splitting for better performance
  - Route-level guards and resolvers
  - SEO-friendly routing
- **Comprehensive Error Handling**
  - Global error interceptor
  - User-friendly error messages
  - Automatic retry mechanisms

### 🎨 UI/UX
- Responsive design
- Modern CSS with gradients and animations
- Form validation with real-time feedback
- Loading states and error messages
- Data test attributes for E2E testing

### 🚀 Performance
- Client-side caching service
- Lazy loading routes
- OnPush change detection
- Performance monitoring
- Optimized build configuration

## Services

- **AuthService**: Authentication and authorization
- **TaskService**: Task and category management
- **CacheService**: Client-side data caching
- **FileService**: File upload and management
- **PerformanceService**: Performance monitoring
- **ErrorHandlerService**: Global error handling

## Testing

- **Unit Tests**: Jasmine/Karma with coverage reports
- **E2E Tests**: Cypress for integration testing
- **Test Coverage**: Comprehensive test coverage
- **CI/CD**: Automated testing pipeline

## Development

```bash
# Start development server
npm start

# Start with Docker backend
npm run start:docker

# Run tests
npm test

# Run E2E tests
npm run e2e

# Build for production
npm run build
```

## Project Structure

```
src/
├── app/
│   ├── core/          # Core services and guards
│   ├── features/      # Feature modules
│   │   ├── auth/      # Authentication
│   │   ├── dashboard/ # Dashboard
│   │   ├── tasks/     # Task management
│   │   └── profile/   # User profile
│   └── shared/        # Shared components
└── environments/      # Environment configurations
```