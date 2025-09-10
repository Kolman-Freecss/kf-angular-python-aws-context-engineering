# Docker Architecture Pattern

## Multi-stage Build Structure

```dockerfile
# Frontend Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
USER nginx
CMD ["nginx", "-g", "daemon off;"]
```

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS production
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Docker Compose Structure

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    environment:
      - API_URL=http://backend:8000
    depends_on:
      - backend
    volumes:
      - frontend_static:/usr/share/nginx/html

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      - db
    volumes:
      - backend_logs:/app/logs

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  frontend_static:
  backend_logs:
  postgres_data:
```

## Environment Configuration

```bash
# .env file
NODE_ENV=production
API_URL=http://localhost:8000
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
JWT_SECRET=your-secret-key
```

## Security Best Practices

1. **Non-root users**: Each service runs as non-root user
2. **Minimal base images**: Use alpine or slim variants
3. **Multi-stage builds**: Separate build and runtime environments
4. **Environment variables**: Use .env files for configuration
5. **Volume management**: Use named volumes for persistent data
