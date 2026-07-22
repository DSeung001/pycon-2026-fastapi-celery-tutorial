import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import (
    ALLOWED_EXTENSIONS,
    CHUNK_SIZE,
    INPUTS_DIR,
    MAX_UPLOAD_BYTES,
    MEDIA_INPUTS_URL,
    MEDIA_OUTPUTS_URL,
    SOURCE_BASENAME,
    ENCODE_TASK,
)

from app.celery_client import celery

router = APIRouter()

# 비동기로 작업을 해야 하는데, FastAPI에서 async로 하면 파이썬의 비동기 이벤트 루프를 사용
# 일반 함수는 싱글 스레드 풀이라서 동기로 진행
# UploadFile은 내부에서 비동기 읽기를 지원해서 UploadFile로 타입 힌트
# 기존에는 바로 리소스만 만들어서 201이 적합했는데,
# 이번엔 인코딩 요청을 수락하는 개념이라 202(Accepted)가 적합
@router.post("/videos", status_code=202)
async def upload_video(file: UploadFile = File(...)):
    # 파일 체크
    if not file.filename:
        raise HTTPException(400, "Missing file")

    # 파일 확장자 체크
    ext = Path(file.filename).suffix.lstrip(".").lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported extension: {ext}")

    # 폴더 생성
    job_id = str(uuid.uuid4())
    job_dir = INPUTS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    dest = job_dir / f"{SOURCE_BASENAME}.{ext}"

    # 파일 저장
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
        # 부분 저장 정리
        if dest.exists():
            dest.unlink()
        job_dir.rmdir()
        raise

    if total == 0:
        dest.unlink()
        job_dir.rmdir()
        raise HTTPException(400, "Empty file")

    # Celery 작업 등록
    try: 
        celery.send_task(
            ENCODE_TASK,
            args=[job_id, ext],
            task_id=job_id, 
        )
    except Exception:
        # 작업 등록 실패 시 파일 삭제
        dest.unlink(missing_ok=True)
        job_dir.rmdir()
        raise HTTPException(500, "Failed to enqueue job")

    source_url = f"{MEDIA_INPUTS_URL}/{job_id}/{SOURCE_BASENAME}.{ext}"
    # celery 작업만 등록하고 반환
    return {
        "job_id": job_id,
        "status": "PENDING",        
        "status_url": f"/api/jobs/{job_id}", # 작업 상태 조회 경로
        "source_url": source_url, # 원본 미디어 경로
    }

# 작업 가져오기
@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    job_dir = INPUTS_DIR / job_id
    if not job_dir.exists():
        raise HTTPException(404, "Job not found")   
    
    # 원본 파일 조회
    sources: list[Path] = list(job_dir.glob(f"{SOURCE_BASENAME}.*"))
    if not sources:
        raise HTTPException(404, "Unknown job")
    ext = sources[0].suffix.lstrip(".")
    source_url = f"{MEDIA_INPUTS_URL}/{job_id}/{SOURCE_BASENAME}.{ext}"

    # Celery 작업 상태 조회, Redis Backend에서 정보 조회
    result = celery.AsyncResult(job_id)
    status = result.state # PENDING / STARTED / SUCCESS / FAILURE

    response = {
        "job_id": job_id,
        "status": status,
        "source_url": source_url,
    }

    if status == "SUCCESS":
        response["hls_url"] = f"{MEDIA_OUTPUTS_URL}/{job_id}/playlist.m3u8"
    elif status == "FAILURE":
        response["error"] = "Video encoding failed"
    return response