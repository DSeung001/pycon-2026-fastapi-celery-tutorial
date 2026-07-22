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


# 비동기로 작업을 해야 하는데, FastAPI에서 async로 하면 파이썬의 비동기 이벤트 루프를 사용
# 일반 함수는 싱글 스레드 풀이라서 동기로 진행
# UploadFile은 내부에서 비동기 읽기를 지원해서 UploadFile로 타입 힌트
# 파일을 바로 만들어 두는 단계라 HTTP 상태코드는 201(Created)이 적합
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
        # with로 자원을 획득하고 사용한 뒤 반드시 반납해야 하는 작업을 안전하고 간결하게 처리
        # 반납 안 하면 메모리 누수로 장기적으로 서비스가 터지는 원인이 될 수 있음
        with dest.open("wb") as out:
            # 청크 단위로 읽어서 저장 — 한 번에 다 받지 않고 안전성 강화
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
