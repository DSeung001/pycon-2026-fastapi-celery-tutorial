from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import (
    INPUTS_DIR,
    MEDIA_INPUTS_URL,
    MEDIA_OUTPUTS_URL,
    OUTPUTS_DIR,
)
from app.routes.videos import router as videos_router

# FastAPI 앱 인스턴스 생성
app = FastAPI(title="Pycon 2026 Video Converter")

# 라우터 등록
app.include_router(videos_router, prefix="/api")

# 입력 및 출력 폴더 생성
INPUTS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# 입력 및 출력 파일 제공
app.mount(MEDIA_INPUTS_URL, StaticFiles(directory=INPUTS_DIR), name="inputs")
app.mount(MEDIA_OUTPUTS_URL, StaticFiles(directory=OUTPUTS_DIR), name="outputs")

# 튜토리얼 페이지 제공
app.mount("/", StaticFiles(directory="static", html=True), name="static")