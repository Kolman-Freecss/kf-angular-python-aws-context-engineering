@echo off
echo Starting hybrid development mode...
echo Starting backend services with Docker...
docker-compose up -d db redis localstack backend celery celery-beat

echo.
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

echo.
echo Services status:
docker-compose ps

echo.
echo Starting frontend with ng serve...
echo Frontend will be available at: http://localhost:4200
echo Backend API is available at: http://localhost:8000
echo.

cd frontend
npm run start:docker