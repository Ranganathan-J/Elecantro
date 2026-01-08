from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Create Celery app
app = Celery('core')

# Load config from Django settings with 'CELERY' namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

app.conf.broker_connection_retry_on_startup = True

# Import monitoring signals (will be loaded when Django is ready)
try:
    from .celery_monitoring import *  # noqa: F401,F403
except ImportError:
    pass  # Monitoring not available in all environments

# Configure periodic tasks
app.conf.beat_schedule = {
    'print-feedback-every-10-seconds': {
        'task': 'data_ingestion.tasks.print_random_feedback',
        'schedule': 10.0,  # Every 10 seconds
    },
    'process-pending-feedbacks-every-minute': {
        'task': 'data_ingestion.tasks.process_pending_feedbacks',
        'schedule': 60.0,  # Every 1 minute
    },
    'cleanup-old-feedbacks-daily': {
        'task': 'data_ingestion.tasks.cleanup_old_feedbacks',
        'schedule': crontab(hour=2, minute=0),  # Every day at 2 AM
    },
    # NEW: Insight generation tasks
    'generate-daily-insights': {
        'task': 'data_ingestion.tasks.daily_insights_generation',
        'schedule': crontab(hour=6, minute=0),  # Every day at 6 AM
    },
    'cleanup-old-insights-weekly': {
        'task': 'data_ingestion.tasks.cleanup_old_insights',
        'schedule': crontab(hour=3, minute=0, day_of_week=1),  # Every Monday at 3 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery is working"""
    print(f'Request: {self.request!r}')
    return 'Celery is working!'