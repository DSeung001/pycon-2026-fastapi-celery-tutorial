from celery import Celery

from app.settings import REDIS_URL

celery_app = Celery(
    "video-worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

