import os
from celery import Celery
from app.config import REDIS_URL

# broker: Redis를 사용하여 작업을 전달하는 브로커
# backend: Redis를 사용하여 작업 결과를 저장하 곳 (잡 진행 상태 기록)
celery = Celery(
    "api",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# Celery의 작업은 backend에서 다음으로 상태가 표시됨
# 기본 값: PENDING / STARTED / RETRY / SUCCESS / FAILURE
celery.conf.update(
    task_track_started=True, # STARTED 상태로 시작
    task_serializer="json", # 작업 데이터를 JSON 직렬화 
    result_serializer="json", # 결과 데이터를 JSON 직렬화
    accept_content=["json"], # 허용 포멧
    timezone="Asia/Seoul", # 시간대
    enable_utc=False, # UTC 사용 여부
)