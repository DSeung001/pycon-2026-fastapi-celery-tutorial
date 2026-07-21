# PyCon 2026 FastAPI + Celery 영상 인코딩

Checkpoint 03: worker에서 FFmpeg로 HLS를 생성하고 상태 API로 확인합니다.

## 실행 (권장: Docker)

```bash
python scripts/dev.py docker
```

브라우저: http://localhost:8000

## 확인

1. 영상 업로드 후 `PENDING` → `STARTED` → `SUCCESS` 전이 확인
2. `data/outputs/{job_id}/playlist.m3u8`와 segment 생성 확인
3. 상태 응답의 `hls_url` 확인

재생 UI는 `checkpoint/04-hls-player`에서 이어서 구현합니다.
