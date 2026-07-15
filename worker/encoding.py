from __future__ import annotations

import subprocess
from pathlib import Path

from app.settings import OUTPUTS_DIR, SAMPLES_DIR


def resolve_source_file(source_name: str) -> Path:
    source_path = (SAMPLES_DIR / source_name).resolve()
    if source_path.parent != SAMPLES_DIR.resolve() or not source_path.exists():
        raise FileNotFoundError("source file not found in samples/")
    return source_path


def run_hls_encoding(job_id: str, source_name: str) -> str:
    source_path = resolve_source_file(source_name)
    target_dir = OUTPUTS_DIR / job_id
    target_dir.mkdir(parents=True, exist_ok=True)

    playlist_path = target_dir / "index.m3u8"
    segment_pattern = str(target_dir / "segment%03d.ts")

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(source_path),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-g",
        "48",
        "-sc_threshold",
        "0",
        "-c:a",
        "aac",
        "-ar",
        "48000",
        "-hls_time",
        "2",
        "-hls_playlist_type",
        "vod",
        "-hls_segment_filename",
        segment_pattern,
        str(playlist_path),
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr.strip()}")
    if not playlist_path.exists():
        raise RuntimeError("encoding finished but index.m3u8 was not created")

    return f"/outputs/{job_id}/index.m3u8"

