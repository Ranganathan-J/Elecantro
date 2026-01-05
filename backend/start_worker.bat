@echo off
echo ========================================
echo Starting Celery Worker for Elecantro
echo ========================================
echo.
echo This worker processes uploaded files in the background.
echo Keep this window open while using the application.
echo.
echo Press Ctrl+C to stop the worker.
echo ========================================
echo.

.venv\Scripts\celery -A core worker -l info -P eventlet

pause
