from celery import Celery
from app.config import REDIS_URL

celery = Celery(
    "worker", 
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

# import 에러 방지
import app.tasks  # noqa: F401