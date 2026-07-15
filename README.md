# PyCon 2026 FastAPI + Celery 튜토리얼 (MVP)

FastAPI API 서버가 인코딩 요청을 받고, Celery Worker가 Redis 큐를 통해 FFmpeg HLS 변환을 수행하는 최소 예제입니다.

## 1) 시작하기

```bash
make up
make sample-video
```

- API: http://localhost:8000
- Web UI: http://localhost:8000

## 2) API

### 상태 확인

```bash
curl http://localhost:8000/health
```

### 인코딩 작업 요청

```bash
curl -X POST http://localhost:8000/jobs \
  -H "content-type: application/json" \
  -d '{"source":"input.mp4"}'
```

응답 예시:

```json
{"job_id":"...","status":"queued"}
```

### 작업 상태 조회

```bash
curl http://localhost:8000/jobs/<job_id>
```

상태는 `queued`, `processing`, `completed`, `failed` 중 하나입니다.

## 3) 핵심 흐름

1. `POST /jobs`는 입력 파일만 검증하고 Celery 작업을 큐에 넣습니다.
2. Worker가 FFmpeg로 `outputs/{job_id}/index.m3u8`를 생성합니다.
3. `GET /jobs/{job_id}`에서 상태와 `output_url`을 확인합니다.

## 4) 정리

```bash
make down
```

