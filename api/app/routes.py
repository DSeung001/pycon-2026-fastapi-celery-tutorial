from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    """앱이 살아 있는지 확인하는 최소 API."""
    return {"status": "ok"}
