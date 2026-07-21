import os
from pathlib import Path

# 경로 설정
DATA_ROOT = Path(os.getenv("DATA_ROOT", "/data"))
INPUTS_DIR = DATA_ROOT / "inputs"
OUTPUTS_DIR = DATA_ROOT / "outputs"
SOURCE_BASENAME = "source"

# 업로드 용량 설정
MB = 1024 * 1024
CHUNK_SIZE = 4 * MB
DEFAULT_MAX_UPLOAD_BYTES = 100 * MB
MAX_UPLOAD_BYTES = int(
    os.getenv("MAX_UPLOAD_BYTES", str(DEFAULT_MAX_UPLOAD_BYTES))
)

# 확장자 설정
ALLOWED_EXTENSIONS = {
    extension.strip().lower()
    for extension in os.getenv("ALLOWED_EXTENSIONS", "mp4,mov,webm").split(",")
    if extension.strip()
}

# 미디어(클라이언트에서 접근 가능) 경로 설정
MEDIA_INPUTS_URL = "/media/inputs"
MEDIA_OUTPUTS_URL = "/media/outputs"
