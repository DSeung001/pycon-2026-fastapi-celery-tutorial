# PyCon 2026 FastAPI + Celery 영상 인코딩

Checkpoint 00: FastAPI 초기 환경을 세팅하고 앱 기동을 확인합니다.

## 실행 (권장: Docker)

```bash
python scripts/dev.py docker
```

브라우저: http://localhost:8000

## 확인

```bash
curl -s http://localhost:8000/api/health
```

성공하면 `{"status":"ok"}`가 반환되고, http://localhost:8000/docs 에서 Swagger UI를 볼 수 있습니다.

이 단계에서는 업로드 API가 아직 없습니다.
다음 단계는 `checkpoint/01-fastapi-upload`입니다.
