from celery import Celery
from database.config import db_settings

celery_app = Celery(
    "worker",
    broker=db_settings.REDIS_URL(9),
    backend=db_settings.REDIS_URL(9),
)

celery_app.autodiscover_tasks(["app.worker"])
