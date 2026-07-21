# PyCon 2026 FastAPI + Celery 영상 인코딩 튜토리얼 개요

## 한 문장 설명

FastAPI 요청 안에서 오래 걸리는 영상 인코딩을 실행하지 않고, Redis와 Celery를 통해 백그라운드 worker로 분리하는 구조를 단계별로 구현합니다.

## 수강 대상

- Python으로 간단한 웹 API를 만들어 본 경험이 있는 참가자
- Celery, 메시지 브로커, 백그라운드 작업이 아직 낯선 참가자
- FFmpeg와 HLS를 깊게 사용해 본 경험은 없어도 됨

## 준비 환경

- Docker를 실행할 수 있는 노트북
- Python과 HTTP API에 대한 기본 이해
- `curl` 또는 유사한 HTTP 클라이언트
- 최신 웹 브라우저

### 세팅 (권장: Docker 실행)

| 항목 | 용도 |
|------|------|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | API · Redis · worker (Compose 포함) |
| [Python 3.13](https://www.python.org/downloads/release/python-3130/) | `scripts/dev.py` 헬퍼 |
| Git | clone · 체크포인트 브랜치 이동 |

```bash
docker --version && docker compose version
python --version   # 3.13.x
git clone https://github.com/DSeung001/pycon-2026-fastapi-celery-tutorial.git
cd pycon-2026-fastapi-celery-tutorial
python scripts/dev.py docker
```

Docker로 돌리면 호스트에 FFmpeg·Redis 설치는 필요 없습니다.

## 학습 목표

참가자는 실습 후 다음 흐름을 설명하고 직접 확인할 수 있어야 합니다.

1. FastAPI가 업로드를 받고 작업 ID를 즉시 반환한다.
2. Redis가 Celery 작업 전달과 상태 조회를 지원한다.
3. Celery worker가 API 프로세스와 분리된 상태에서 FFmpeg를 실행한다.
4. FFmpeg가 영상을 HLS manifest와 segment로 변환한다.
5. 브라우저가 작업 상태를 polling하고 완료된 HLS 영상을 재생한다.
6. 원본 영상과 인코딩 결과를 비교한다.

## 핵심 메시지

오래 걸리는 작업을 HTTP 요청 안에서 직접 실행하면 다음 문제가 발생할 수 있습니다.

- 클라이언트 또는 프록시 타임아웃
- API worker 장시간 점유
- 사용자 응답 지연
- 실패와 재시도 처리의 복잡성 증가

따라서 요청을 받는 API와 실제 작업을 수행하는 worker의 책임을 분리합니다.

## 구성 요소

- **FastAPI**: 업로드, 작업 생성, 작업 상태 API, 정적 페이지
- **Redis**: Celery broker와 result backend
- **Celery**: 비동기 작업 실행과 상태 관리
- **FFmpeg**: 입력 영상을 HLS로 변환
- **Docker Compose**: 참가자 환경 통일

## 실습 흐름

1. FastAPI 앱을 기동하고 `/docs`, `/api/health`로 환경을 확인한다.
2. FastAPI 업로드 API를 만든다.
3. `curl`로 영상을 업로드하고 저장 결과를 확인한다.
4. Redis와 Celery worker를 연결한다.
5. API가 작업을 enqueue하고 즉시 `202 Accepted`를 반환하도록 변경한다.
6. worker에서 FFmpeg를 실행한다.
7. 작업별 디렉터리에 HLS manifest와 segment를 생성한다.
8. 상태 API로 `PENDING`, `STARTED`, `SUCCESS`, `FAILURE`를 확인한다.
9. 웹 페이지에서 상태를 polling한다.
10. 원본 영상과 HLS 결과를 나란히 재생한다.

## 체크포인트

- `checkpoint/00-fastapi-setup`: FastAPI 초기 기동과 환경 확인
- `checkpoint/01-fastapi-upload`: FastAPI와 업로드 저장
- `checkpoint/02-celery-redis`: Redis, Celery, 비동기 상태
- `checkpoint/03-ffmpeg-hls`: worker FFmpeg 실행과 실패 처리
- `checkpoint/04-hls-player`: HLS 플레이어 UI(제공 코드). GitHub `static/`을 받아 확인

참가자가 환경 문제나 코드 오류로 막히면 다음 체크포인트 브랜치로 이동해 실습을 이어갈 수 있어야 합니다.

## 초급 실습에서 제한할 범위

실습 중에는 다음을 구현하지 않습니다.

- 적응형 비트레이트와 여러 해상도
- 인증과 다중 사용자 권한
- 데이터베이스 기반 영구 작업 상태
- S3 등 외부 스토리지
- 자동 재시도와 중복 실행 방지 체계
- 운영용 모니터링과 자동 파일 정리

구조를 이해하는 데 필요하지 않은 추상화와 운영 기능은 핵심 흐름을 가릴 수 있기 때문입니다.

## 시간이 남을 때 다룰 운영 주제

실제 영상 플랫폼 경험을 바탕으로 다음 항목을 개념 수준에서 소개합니다.

- 긴 인코딩의 타임아웃과 작업 제한 시간
- Celery 재시도와 중복 실행 가능성
- idempotency
- Redis broker 설정
- worker concurrency와 prefetch
- 작업 상태 영속화
- 업로드 크기 제한과 파일 정리 정책
- FFmpeg 옵션 조정
- WebM과 VFR 영상의 FPS metadata 문제
- 로그, 지표, 알림