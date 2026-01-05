@echo off
echo ========================================
echo   Elecantro Backend - Complete Startup
echo ========================================
echo.
echo This will start:
echo   1. Django Development Server (Port 8000)
echo   2. Celery Worker (Background Processing)
echo.
echo Make sure Redis is running before proceeding!
echo (Docker: docker run -d -p 6379:6379 redis)
echo.
pause

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo.
echo Starting services...
echo.

REM Start Django Server in new window
start "Django Server - Port 8000" cmd /k "cd /d "%SCRIPT_DIR%" && .venv\Scripts\activate && echo Starting Django Server... && python manage.py runserver"

REM Wait a moment for Django to start
timeout /t 3 /nobreak >nul

REM Start Celery Worker in new window
start "Celery Worker - Background Tasks" cmd /k "cd /d "%SCRIPT_DIR%" && .venv\Scripts\activate && echo Starting Celery Worker... && celery -A core worker -l info -P eventlet"

echo.
echo ========================================
echo   All services started!
echo ========================================
echo.
echo You should now see 2 new windows:
echo   - Django Server (http://localhost:8000)
echo   - Celery Worker (Processing uploads)
echo.
echo To stop all services:
echo   - Close each terminal window OR press Ctrl+C in each
echo.
echo You can close this window now.
echo ========================================
pause
