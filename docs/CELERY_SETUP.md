# Celery Worker Setup - Fixing "Processing 0%" Issue

## The Problem
When you upload a file, it gets stuck at "Processing 0%" because the **Celery Worker** isn't running or can't connect to Redis.

## Solution: Choose One Option

---

### ✅ **OPTION 1: Install Local Redis (Best for Development)**

#### Step 1: Install Redis

**Using Docker (Easiest):**
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

**Using Windows Installer:**
1. Download: https://github.com/microsoftarchive/redis/releases
2. Install and run Redis server

#### Step 2: Update Environment Variables
Edit `backend/.env` and change:
```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

#### Step 3: Start the Worker
```bash
cd backend
start_worker.bat
```

---

### ⚡ **OPTION 2: Use Database as Queue (Quick Fix)**

This is slower but works without Redis installation.

#### Step 1: Update Settings
Add to `backend/core/settings.py`:
```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps ...
    'django_celery_results',
]

# Change Celery config
CELERY_BROKER_URL = 'django://'  # Use database
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
```

#### Step 2: Run Migrations
```bash
cd backend
.venv\Scripts\activate
python manage.py migrate django_celery_results
```

#### Step 3: Install Kombu Transport
```bash
pip install kombu[sqlalchemy]
```

#### Step 4: Start the Worker
```bash
cd backend
start_worker.bat
```

---

## How to Verify It's Working

1. **Check Worker Terminal**: You should see:
   ```
   [tasks]
     . process_bulk_feedbacks
     . process_feedback_with_ai
   
   celery@YourPC ready.
   ```

2. **Upload a File**: The status should change from:
   - "Uploading..." → "Processing" → "Completed"

3. **Check Dashboard**: You should see data appear within 30-60 seconds

---

## Current Status

✅ Celery is installed
✅ Eventlet is installed (Windows support)
✅ Worker script created (`start_worker.bat`)
⚠️ **Redis connection needed** - Choose Option 1 or 2 above

---

## Troubleshooting

**Worker shows "Cannot connect to redis"**
→ Redis isn't running. Use Option 1 (install Redis) or Option 2 (use database)

**Worker starts but tasks don't process**
→ Make sure Django server is also running (`python manage.py runserver`)

**"ImportError" when starting worker**
→ Make sure virtual environment is activated: `.venv\Scripts\activate`

**Still stuck at 0%?**
→ Check both terminals are running (Django + Worker)
→ Check browser console for errors (F12)
