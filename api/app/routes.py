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
)

router = APIRouter()


@router.post("/videos", status_code=201)
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

    source_url = f"{MEDIA_INPUTS_URL}/{job_id}/{SOURCE_BASENAME}.{ext}"
    return {
        "job_id": job_id,
        "source_url": source_url,
    }
