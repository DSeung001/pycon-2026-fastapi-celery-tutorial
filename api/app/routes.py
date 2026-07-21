import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import (
    ALLOWED_EXTENSIONS,
    CHUNK_SIZE,
    INPUTS_DIR,
    MAX_UPLOAD_BYTES,
    MEDIA_INPUTS_URL,
    SOURCE_BASENAME,
    ENCODE_TASK,
)

from app.celery_client import celery

router = APIRouter()


@router.post("/videos", status_code=202)
async def upload_video(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "Missing file")

    ext = Path(file.filename).suffix.lstrip(".").lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported extension: {ext}")

    job_id = str(uuid.uuid4())
    job_dir = INPUTS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    dest = job_dir / f"{SOURCE_BASENAME}.{ext}"

    total = 0
    try:
        with dest.open("wb") as out:
            while chunk := await file.read(CHUNK_SIZE):
                total += len(chunk)
                if total > MAX_UPLOAD_BYTES:
                    raise HTTPException(413, "Upload too large")
                out.write(chunk)
    except Exception:
        if dest.exists():
            dest.unlink()
        job_dir.rmdir()
        raise

    if total == 0:
        dest.unlink()
        job_dir.rmdir()
        raise HTTPException(400, "Empty file")

    try:
        celery.send_task(
            ENCODE_TASK,
            args=[job_id, ext],
            task_id=job_id,
        )
    except Exception:
        dest.unlink(missing_ok=True)
        job_dir.rmdir()
        raise HTTPException(500, "Failed to enqueue job")

    source_url = f"{MEDIA_INPUTS_URL}/{job_id}/{SOURCE_BASENAME}.{ext}"
    return {
        "job_id": job_id,
        "status": "PENDING",
        "status_url": f"/api/jobs/{job_id}",
        "source_url": source_url,
    }


@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    job_dir = INPUTS_DIR / job_id
    if not job_dir.exists():
        raise HTTPException(404, "Job not found")

    sources: list[Path] = list(job_dir.glob(f"{SOURCE_BASENAME}.*"))
    if not sources:
        raise HTTPException(404, "Unknown job")
    ext = sources[0].suffix.lstrip(".")
    source_url = f"{MEDIA_INPUTS_URL}/{job_id}/{SOURCE_BASENAME}.{ext}"

    result = celery.AsyncResult(job_id)
    status = result.state

    response = {
        "job_id": job_id,
        "status": status,
        "source_url": source_url,
    }

    if status == "FAILURE":
        response["error"] = "Background task failed"
    return response
