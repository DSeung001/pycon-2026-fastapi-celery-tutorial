import os
from pathlib import Path

DATA_ROOT = Path(os.getenv("DATA_ROOT", "/data"))
INPUTS_DIR = DATA_ROOT / "inputs"
OUTPUTS_DIR = DATA_ROOT / "outputs"

MB = 1024 * 1024
CHUNK_SIZE = 4 * MB
DEFAULT_MAX_UPLOAD_BYTES = 500 * MB
MAX_UPLOAD_BYTES = DEFAULT_MAX_UPLOAD_BYTES

ALLOWED_EXTENSIONS = {"mp4", "mov", "webm"}

MEDIA_INPUTS_URL = "/media/inputs"
MEDIA_OUTPUTS_URL = "/media/outputs"
SOURCE_BASENAME = "source"