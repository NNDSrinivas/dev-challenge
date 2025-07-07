import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

app = Celery("api")

# pull in configuration from Django settings, using a CELERY_ prefix in settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# auto-discover async tasks in INSTALLED_APPS
app.autodiscover_tasks()
