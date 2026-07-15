from __future__ import annotations

import subprocess

from app.settings import SAMPLES_DIR

SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
output_file = SAMPLES_DIR / "input.mp4"

command = [
    "ffmpeg",
    "-y",
    "-f",
    "lavfi",
    "-i",
    "testsrc=duration=5:size=640x360:rate=30",
    "-pix_fmt",
    "yuv420p",
    str(output_file),
]

subprocess.run(command, check=True)
print(f"created: {output_file}")

