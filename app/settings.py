from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLES_DIR = BASE_DIR / "samples"
OUTPUTS_DIR = BASE_DIR / "outputs"
WEB_DIR = BASE_DIR / "web"

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

