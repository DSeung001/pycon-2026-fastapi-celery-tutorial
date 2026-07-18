## 실행 (권장: Docker)

Docker로 돌리면 FFmpeg를 호스트에 설치할 필요가 없습니다. worker 이미지에 포함되어 있습니다.

```bash
python scripts/dev.py docker
```

브라우저: http://localhost:8000

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