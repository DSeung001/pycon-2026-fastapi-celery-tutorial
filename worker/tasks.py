from __future__ import annotations

from worker.celery_app import celery_app
from worker.encoding import run_hls_encoding


@celery_app.task(name="encode_to_hls", bind=True)
def encode_to_hls(self, source_name: str) -> dict[str, str]:
    job_id = self.request.id
    output_url = run_hls_encoding(job_id=job_id, source_name=source_name)
    return {"job_id": job_id, "output_url": output_url}
