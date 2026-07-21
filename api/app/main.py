from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import router as api_router

# FastAPI 앱 인스턴스 생성
app = FastAPI(title="Pycon 2026 Video Converter")

# 라우터 등록 (/api/*)
app.include_router(api_router, prefix="/api")

# 튜토리얼 페이지 제공
app.mount("/", StaticFiles(directory="static", html=True), name="static")
