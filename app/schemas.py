from pydantic import BaseModel


class JobCreateRequest(BaseModel):
    source: str = "input.mp4"


class JobCreateResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    output_url: str | None = None
    error: str | None = None

