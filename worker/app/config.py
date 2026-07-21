import os
from pathlib import Path

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Celery 설정
ENCODE_TASK = "encode_video"