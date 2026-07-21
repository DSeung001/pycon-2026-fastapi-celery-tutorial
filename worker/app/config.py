import os
from pathlib import Path

# 경로 설정
DATA_ROOT = Path(os.getenv("DATA_ROOT", "/data"))
INPUTS_DIR = DATA_ROOT / "inputs"
OUTPUTS_DIR = DATA_ROOT / "outputs"
SOURCE_BASENAME = "source"

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Celery 설정
ENCODE_TASK = "encode_video"
