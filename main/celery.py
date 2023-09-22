import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

app = Celery("main")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "Send_overdue_debt_email_every_day": {
        "task": "send_overdue_debt_email",
        "schedule": crontab(hour="0-1", minute="*/5"),
    },
    "Send_overdue_debt_telegram_every_day": {
        "task": "send_overdue_debt_telegram",
        "schedule": crontab(hour="0-1", minute="*/5"),
    },
}
