from __future__ import absolute_import
import os
from efsilonquest.core.celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task
def debug_task():
    print("Celery is working!")