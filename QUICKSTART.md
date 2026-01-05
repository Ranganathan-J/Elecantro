# Quick Start Guide - Elecantro

## 🐳 DOCKER WAY - Containerized Startup

If you have Docker installed, this is the most reliable way to run everything:

```bash
docker-compose up --build
```

This will start:
- ✅ **PostgreSQL Database**
- ✅ **Redis**
- ✅ **Django Backend** (http://localhost:8000)
- ✅ **Celery Worker** (Background AI processing)
- ✅ **React Frontend** (http://localhost:5173 or http://localhost)

---

## 🚀 EASIEST WAY - One-Click Startup (Windows)

## Manual Startup (If Needed)

### Backend Only
Double-click: `backend/start_all.bat`

OR manually:

### Step 1: Start Backend Server
```bash
cd backend
.venv\Scripts\activate
python manage.py runserver
```
**Leave this terminal open!**

### Step 2: Start Background Worker ⚡ (REQUIRED!)
**Option A - Easy:**
```bash
cd backend
start_worker.bat
```

**Option B - Manual:**
```bash
cd backend
.venv\Scripts\activate
celery -A core worker -l info -P eventlet
```
**Leave this terminal open!**

### Step 3: Start Frontend
```bash
cd frontend
npm run dev
```
**Leave this terminal open!**

### Step 4: Open Browser
Navigate to: `http://localhost:5173`

---

## Why Do I Need the Worker?

The **Celery Worker** processes uploaded files in the background:
- ✅ **With Worker**: Files upload instantly, processing happens in background
- ❌ **Without Worker**: Files get stuck at "Processing 0%" forever

---

## Troubleshooting

**Problem:** Upload stuck at "Processing 0%"
**Solution:** Make sure `start_worker.bat` is running in a separate terminal

**Problem:** "Connection refused" error
**Solution:** Ensure Redis is running (check Docker or install Redis locally)

**Problem:** Worker won't start
**Solution:** Run `pip install eventlet` in your virtual environment

---

## What Each Terminal Does:

1. **Terminal 1 (Django)**: Handles web requests (login, upload, API calls)
2. **Terminal 2 (Celery Worker)**: Processes files and runs AI analysis
3. **Terminal 3 (Frontend)**: Serves the React UI

All three must be running simultaneously!
