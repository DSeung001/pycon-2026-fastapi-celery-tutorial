import logging
import subprocess

from app.celery_app import celery
from app.config import (
    INPUTS_DIR, 
    OUTPUTS_DIR, 
    SOURCE_BASENAME, 
    ENCODE_TASK,
)

logger = logging.getLogger(__name__)

@celery.task(name=ENCODE_TASK)
def encode_video(job_id: str, ext: str):
    source = INPUTS_DIR / job_id / f"{SOURCE_BASENAME}.{ext}"
    out_dir = OUTPUTS_DIR / job_id
    playlist = out_dir / "playlist.m3u8"

    if not source.is_file():
        raise FileNotFoundError(f"source missing: {source}")

    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y", "-i", str(source),
        "-c:v", "libx264", "-c:a", "aac",
        "-start_number", "0",
        "-hls_time", "2",
        "-hls_list_size", "0",
        "-f", "hls",
        "-hls_segment_filename", str(out_dir / "segment_%03d.ts"),
        str(playlist),
    ]
    
    try:
        # ffmpeg 실행
        completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if completed.stderr:
            logger.info("ffmpeg stderr:\n%s", completed.stderr[-2000:])
    except FileNotFoundError as e:
        # ffmpeg 미설치 시
        raise RuntimeError("ffmpeg not found") from e
    except subprocess.CalledProcessError as e:
        # ffmpeg 실행 실패 시
        logger.error("ffmpeg failed:\n%s", (e.stderr or "")[-2000:])
        raise RuntimeError("ffmpeg failed") from e

    # HLS 파일 없을 때     
    if not playlist.is_file():
        raise RuntimeError("playlist.m3u8 missing")

    return {"hls_path": str(playlist)}