from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import INPUTS_DIR, OUTPUTS_DIR, MEDIA_INPUTS_URL, MEDIA_OUTPUTS_URL
from app.routes.videos import router as videos_router

# Fast API 앱 인스턴스 생성
app = FastAPI(title="Pycon 2026 Video Converter")
# 라우터 등록
app.include_router(videos_router, prefix="/api")

# 업로드 폴더 생성  
INPUTS_DIR.mkdir(parents=True, exist_ok=True)
# 출력 폴더 폴더
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# 정적 파일(퍼블리싱) 서버 마운트, static 폴더 안의 파일을 정적 파일로 서비스해줌
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# 업로드 파일 저장 폴더 마운트
app.mount("/media/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")
app.mount(MEDIA_INPUTS_URL, StaticFiles(directory=INPUTS_DIR), name="inputs")
app.mount(MEDIA_OUTPUTS_URL, StaticFiles(directory=OUTPUTS_DIR), name="outputs")