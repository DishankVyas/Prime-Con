from celery import Celery
from config import settings

celery_app = Celery(
  "primecon",
  broker=settings.REDIS_URL,
  backend=settings.REDIS_URL,
  include=["routers.mining"]
)
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.result_expires = 3600
