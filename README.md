## 실행 (권장: Docker)

Docker로 돌리면 FFmpeg를 호스트에 설치할 필요가 없습니다. worker 이미지에 포함되어 있습니다.

```bash
python scripts/dev.py docker
```

브라우저: http://localhost:8000

## 체크포인트 실습

환경은 미리 세팅된 상태로 두고, 막히면 해당 체크포인트 브랜치로 이동해 이어서 진행합니다.

```bash
git fetch origin
git switch checkpoint/00-fastapi-setup
python scripts/dev.py docker
```

| 브랜치 | 학습 내용 | 성공 기준 |
|--------|-----------|-----------|
| `checkpoint/00-fastapi-setup` | FastAPI 초기 기동 | `/api/health`와 `/docs` 확인 |
| `checkpoint/01-fastapi-upload` | FastAPI 업로드와 원본 저장 | `job_id`와 `data/inputs/{job_id}/` 확인 |
| `checkpoint/02-celery-redis` | Redis enqueue와 상태 조회 | `PENDING` → `SUCCESS`, worker 로그 확인 |
| `checkpoint/03-ffmpeg-hls` | worker FFmpeg HLS 인코딩 | `playlist.m3u8`와 `hls_url` 확인 |
| `checkpoint/04-hls-player` | polling과 원본/결과 재생 | 브라우저에서 HLS 재생 |

완성본은 `main`과 `checkpoint/04-hls-player`입니다.

## 로컬 실행

로컬에서 API·worker를 나눠 돌릴 때는 **호스트에 FFmpeg 설치가 필요**합니다.

### 1. FFmpeg 설치

| OS | 명령 |
|----|------|
| macOS | `brew install ffmpeg` |
| Windows | `winget install ffmpeg` |
| 확인 | `ffmpeg -version` |

### 2. 프로세스 기동

터미널을 세 개 열어 각각 실행합니다.

```bash
python scripts/dev.py redis
python scripts/dev.py worker   # 호스트에 ffmpeg 필요
python scripts/dev.py api
```

의존성만 설치하려면:

```bash
python scripts/dev.py install
```
