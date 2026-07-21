# PyCon 2026 FastAPI + Celery 영상 인코딩

Checkpoint 02: Redis와 Celery로 백그라운드 작업을 enqueue하고 상태를 조회합니다.

## 실행 (권장: Docker)

```bash
python scripts/dev.py docker
```

브라우저: http://localhost:8000

## 확인

1. 업로드 직후 `202`와 `job_id`를 받는다
2. `GET /api/jobs/{job_id}`로 `PENDING` / `STARTED` / `SUCCESS`를 확인한다
3. worker 로그에 stub 작업 수신/완료가 보인다

이 단계의 worker는 FFmpeg 없이 `time.sleep` stub만 실행합니다.
실제 인코딩은 `checkpoint/03-ffmpeg-hls`에서 연결합니다.
