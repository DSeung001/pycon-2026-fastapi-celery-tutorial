# PyCon 2026 FastAPI + Celery 영상 인코딩

Checkpoint 01: FastAPI로 영상을 업로드하고 `job_id` 아래에 저장합니다.

## 실행 (권장: Docker)

```bash
python scripts/dev.py docker
```

브라우저: http://localhost:8000

## 확인

```bash
curl -i -F "file=@samples/sample.mp4" http://localhost:8000/api/videos
```

성공하면 `job_id`와 `source_url`이 반환되고, `data/inputs/{job_id}/`에 원본이 저장됩니다.

이 단계에서는 Redis, Celery, FFmpeg가 필요 없습니다.
다음 단계는 `checkpoint/02-celery-redis`입니다.
