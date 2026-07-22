import logging
import time

from app.celery_app import celery
from app.config import ENCODE_TASK

logger = logging.getLogger(__name__)


# 스텁은 미구현 로직을 대신하는 임시 코드
@celery.task(name=ENCODE_TASK)
def encode_video(job_id: str, ext: str):
    """Checkpoint 02용 stub 작업. 실제 FFmpeg는 Checkpoint 03에서 연결한다."""
    logger.info("stub encode started job_id=%s ext=%s", job_id, ext)
    time.sleep(2)
    logger.info("stub encode finished job_id=%s", job_id)
    return {"job_id": job_id, "stub": True}
