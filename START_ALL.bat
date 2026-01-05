@echo off
echo ========================================
echo   Elecantro - FULL STACK STARTUP
echo ========================================
echo.
echo This will start ALL services needed:
echo   [Backend]
echo   1. Django Server (Port 8000)
echo   2. Celery Worker (Background Tasks)
echo.
echo   [Frontend]
echo   3. React Dev Server (Port 5173)
echo.
echo ========================================
echo.

REM Check if Redis is needed
echo Checking Redis connection...
echo.
echo Do you have Redis running?
echo   [1] Yes, Redis is already running
echo   [2] No, start Redis via Docker for me
echo   [3] Skip Redis check (use database queue)
echo.
set /p REDIS_CHOICE="Enter choice (1/2/3): "

if "%REDIS_CHOICE%"=="2" (
    echo.
    echo Starting Redis via Docker...
    docker run -d -p 6379:6379 --name elecantro-redis redis:latest
    timeout /t 3 /nobreak >nul
    echo Redis started!
)

echo.
echo ========================================
echo Starting Backend Services...
echo ========================================

REM Get script directory
set BACKEND_DIR=%~dp0backend
set FRONTEND_DIR=%~dp0frontend

REM Start Django Server
start "Elecantro - Django Server" cmd /k "cd /d "%BACKEND_DIR%" && .venv\Scripts\activate && echo [DJANGO] Starting on http://localhost:8000 && python manage.py runserver"

REM Wait for Django to initialize
timeout /t 3 /nobreak >nul

REM Start Celery Worker
start "Elecantro - Celery Worker" cmd /k "cd /d "%BACKEND_DIR%" && .venv\Scripts\activate && echo [CELERY] Starting background worker... && celery -A core worker -l info -P eventlet"

REM Wait a moment
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo Starting Frontend...
echo ========================================

REM Start Frontend Dev Server
start "Elecantro - React Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && echo [REACT] Starting on http://localhost:5173 && npm run dev"

echo.
echo ========================================
echo   ALL SERVICES STARTED!
echo ========================================
echo.
echo You should now see 3 new windows:
echo   1. Django Server    - http://localhost:8000
echo   2. Celery Worker    - Processing uploads
echo   3. React Frontend   - http://localhost:5173
echo.
echo Open your browser to: http://localhost:5173
echo.
echo To stop all services:
echo   - Close each terminal window
echo   - OR press Ctrl+C in each window
echo.
echo ========================================
echo.
pause
