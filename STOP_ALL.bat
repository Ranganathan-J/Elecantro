@echo off
echo ========================================
echo   Stopping Elecantro Services
echo ========================================
echo.
echo This will attempt to close all Elecantro windows.
echo.
pause

REM Kill Django server (port 8000)
echo Stopping Django server...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /F /PID %%a 2>nul

REM Kill Celery workers
echo Stopping Celery workers...
taskkill /F /IM celery.exe 2>nul

REM Kill Redis (if running locally, not Docker)
echo Stopping Redis (if running)...
taskkill /F /IM redis-server.exe 2>nul

REM Kill Node dev server (port 5173)
echo Stopping React dev server...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5173" ^| find "LISTENING"') do taskkill /F /PID %%a 2>nul

echo.
echo ========================================
echo   All services stopped!
echo ========================================
echo.
echo Note: If you started Redis via Docker, stop it with:
echo   docker stop elecantro-redis
echo   docker rm elecantro-redis
echo.
pause
