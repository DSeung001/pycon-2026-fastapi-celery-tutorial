from __future__ import annotations

from pathlib import Path

from celery.result import AsyncResult
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import JobCreateRequest, JobCreateResponse, JobStatusResponse
from app.settings import OUTPUTS_DIR, SAMPLES_DIR, WEB_DIR
from worker.tasks import encode_to_hls

app = FastAPI(title="PyCon 2026 FastAPI + Celery Tutorial")

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")
app.mount("/samples", StaticFiles(directory=SAMPLES_DIR), name="samples")
app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")


@app.get("/", include_in_schema=False)
def read_index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _resolve_source_file(filename: str) -> Path:
    candidate = (SAMPLES_DIR / filename).resolve()
    if candidate.parent != SAMPLES_DIR.resolve() or not candidate.exists():
        raise HTTPException(status_code=400, detail="source file not found in samples/")
    return candidate


def _map_state(raw_state: str) -> str:
    if raw_state == "PENDING":
        return "queued"
    if raw_state in {"STARTED", "RETRY"}:
        return "processing"
    if raw_state == "SUCCESS":
        return "completed"
    if raw_state in {"FAILURE", "REVOKED"}:
        return "failed"
    return "queued"


@app.post("/jobs", response_model=JobCreateResponse)
def create_job(payload: JobCreateRequest) -> JobCreateResponse:
    _resolve_source_file(payload.source)
    task = encode_to_hls.delay(payload.source)
    return JobCreateResponse(job_id=task.id, status="queued")


@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str) -> JobStatusResponse:
    result = AsyncResult(job_id, app=encode_to_hls.app)
    status = _map_state(result.state)

    output_url: str | None = None
    error: str | None = None

    if result.state == "SUCCESS":
        payload = result.result or {}
        output_url = payload.get("output_url")
    elif result.state in {"FAILURE", "REVOKED"}:
        error = str(result.result)

    return JobStatusResponse(
        job_id=job_id,
        status=status,
        output_url=output_url,
        error=error,
    )

