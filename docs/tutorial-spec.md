# PyCon 2026 FastAPI + Celery Video Encoding Tutorial Specification

## 1. Purpose

This beginner hands-on tutorial demonstrates why long-running work should not execute inside an HTTP request. Participants upload a video to FastAPI, receive a job ID immediately, and observe a Celery worker run FFmpeg to produce HLS output.

The final browser page compares the uploaded source with the encoded HLS result.

## 2. Audience and prerequisites

Audience:

- Comfortable with basic Python and HTTP APIs.
- New to Celery, brokers, result backends, and background workers.
- Not expected to know FFmpeg or HLS in depth.

Prerequisites:

- Laptop capable of running Docker.
- Docker Desktop (Docker Compose included).
- Python 3.13 on the host for `scripts/dev.py` (container images also use Python 3.13).
- Git for clone and checkpoint branches.
- `curl` or an equivalent HTTP client.
- A modern browser.

Setup (recommended Docker path): install Docker Desktop, Python 3.13, and Git; clone the repo; run `python scripts/dev.py docker`. Host FFmpeg/Redis are not required when using Docker.

## 3. Learning outcomes

By the end, participants should be able to explain:

1. Why long-running encoding should not block an HTTP request.
2. The separate responsibilities of FastAPI, Redis, Celery, and FFmpeg.
3. How an API creates a job and returns before the job finishes.
4. How a worker receives the job and writes shared output.
5. How a client polls status and consumes a completed HLS result.
6. Why failure state, duplicate execution, retries, and cleanup matter in production.

## 4. System flow

```text
curl or browser
      |
      | POST /api/videos
      v
FastAPI API
      |  save source under job_id
      |  enqueue encode task
      |  return 202 + job_id
      v
Redis broker/result backend
      |
      v
Celery worker
      |  run FFmpeg
      v
data/outputs/{job_id}/playlist.m3u8 + segments
      ^
      |
Browser polls GET /api/jobs/{job_id}
      |
      +-- source player
      +-- HLS result player
```

## 5. Public API contract

Keep this contract stable across the complete implementation. Earlier checkpoints may return a subset only where the checkpoint explicitly has not introduced a field yet.

### 5.1 Create an encoding job

```http
POST /api/videos
Content-Type: multipart/form-data
```

Form field:

- `file`: uploaded video

Required behavior:

- Generate a UUID4 job ID.
- Store the upload before enqueueing.
- Enqueue the worker task.
- Return without waiting for encoding.
- Respond with HTTP `202 Accepted`.

Example response:

```json
{
  "job_id": "671dadc1-1c01-48ee-87c4-ea809ec2ddd4",
  "status": "PENDING",
  "status_url": "/api/jobs/671dadc1-1c01-48ee-87c4-ea809ec2ddd4",
  "source_url": "/media/inputs/671dadc1-1c01-48ee-87c4-ea809ec2ddd4/source.mp4"
}
```

The server supplies URLs. The browser must not derive them from filesystem assumptions.

### 5.2 Read job status

```http
GET /api/jobs/{job_id}
```

Public states:

- `PENDING`: accepted or waiting for a worker
- `STARTED`: worker began processing
- `SUCCESS`: HLS output is ready
- `FAILURE`: processing failed

Pending response:

```json
{
  "job_id": "671dadc1-1c01-48ee-87c4-ea809ec2ddd4",
  "status": "PENDING",
  "source_url": "/media/inputs/671dadc1-1c01-48ee-87c4-ea809ec2ddd4/source.mp4"
}
```

Started response:

```json
{
  "job_id": "671dadc1-1c01-48ee-87c4-ea809ec2ddd4",
  "status": "STARTED",
  "source_url": "/media/inputs/671dadc1-1c01-48ee-87c4-ea809ec2ddd4/source.mp4"
}
```

Success response:

```json
{
  "job_id": "671dadc1-1c01-48ee-87c4-ea809ec2ddd4",
  "status": "SUCCESS",
  "source_url": "/media/inputs/671dadc1-1c01-48ee-87c4-ea809ec2ddd4/source.mp4",
  "hls_url": "/media/outputs/671dadc1-1c01-48ee-87c4-ea809ec2ddd4/playlist.m3u8"
}
```

Failure response:

```json
{
  "job_id": "671dadc1-1c01-48ee-87c4-ea809ec2ddd4",
  "status": "FAILURE",
  "source_url": "/media/inputs/671dadc1-1c01-48ee-87c4-ea809ec2ddd4/source.mp4",
  "error": "Video encoding failed. Check the worker log for details."
}
```

Unknown job:

```http
HTTP/1.1 404 Not Found
```

A raw Celery `PENDING` value is not sufficient proof that a job exists. The API should also confirm the job's input directory or equivalent local marker exists.

## 6. Storage contract

Logical layout:

```text
data/
├── inputs/
│   └── {job_id}/
│       └── source.{normalized_extension}
└── outputs/
    └── {job_id}/
        ├── playlist.m3u8
        ├── segment_000.ts
        ├── segment_001.ts
        └── ...
```

Rules:

- Use UUID job directories.
- Normalize extensions to lowercase.
- Do not preserve the client filename as a trusted path.
- Allow only configured video extensions, initially `mp4`, `mov`, and `webm` unless the implementation intentionally narrows the workshop to MP4.
- Stream uploads in chunks.
- Configure the maximum upload size through an environment variable.
- Remove partial uploads when validation fails during streaming.
- Mount the same `data` paths at identical locations in the API and worker containers.
- Serve media only from the configured input/output roots.

## 7. Celery contract

Suggested configuration for the teaching implementation:

- Redis broker.
- Redis result backend.
- `task_track_started = True` once status polling is introduced.
- JSON task serialization.
- No automatic task retry in the beginner path.

The task may receive:

- `job_id`
- generated source path or normalized source extension

It must not receive an uploaded file object or construct paths from arbitrary client values.

Successful task result should contain only data needed to build or confirm the response, for example:

```json
{
  "hls_path": "/data/outputs/{job_id}/playlist.m3u8"
}
```

## 8. FFmpeg contract

The initial command should be easy to read and produce one HLS rendition. Exact codec parameters can be tuned for the sample video, but the implementation must preserve these properties:

- Input is the stored job source.
- Output is `playlist.m3u8` under the job output directory.
- Segment names are deterministic.
- Invocation uses an argument array and never a shell.
- Non-zero exit is a task failure.
- Missing manifest is a task failure even if the process exits zero.
- Worker logs include useful stderr without sending the complete output to the browser.

Do not add multiple resolutions, an adaptive bitrate master playlist, GPU encoding, or cloud storage to the core workshop.

## 9. Frontend contract

The final static page should:

1. Accept or identify a created job.
2. Display the source video using the server-provided source URL.
3. Poll the status endpoint at a modest interval such as 1-2 seconds.
4. Show pending and started states.
5. Stop polling on success or failure.
6. On success, initialize HLS playback.
7. Prefer native HLS support and use hls.js as fallback.
8. Show a clear error when playback is unsupported or encoding fails.
9. Keep source and result players visible for comparison.

The UI must avoid duplicate timers and must destroy an old hls.js instance before starting another job.

## 10. Error cases required in the tutorial implementation

Handle at least:

- Missing multipart file.
- Empty upload.
- Unsupported extension.
- Upload exceeding the configured size limit.
- Failure to persist the source.
- Failure to enqueue the task.
- Unknown job ID.
- Missing source in the worker.
- FFmpeg executable unavailable.
- FFmpeg non-zero exit.
- Missing HLS manifest.
- Status polling network failure.
- Browser HLS playback failure.

The browser receives concise errors. Detailed diagnostics remain in API or worker logs.

## 11. Checkpoint sequence

1. `checkpoint/01-fastapi-upload`
2. `checkpoint/02-celery-redis`
3. `checkpoint/03-ffmpeg-hls`
4. `checkpoint/04-hls-player`

The complete implementation is built and verified on `main` first. Each checkpoint is then validated independently so participants can switch branches after getting blocked.

Detailed acceptance checks are in `docs/checkpoint-acceptance.md`.

## 12. Definition of done for `main`

The complete tutorial is done when:

1. `docker compose up --build` starts the API, Redis, and worker.
2. Uploading a supported sample returns HTTP 202 quickly.
3. The response contains a job ID and usable status/source URLs.
4. The worker receives the task and runs FFmpeg.
5. The status transitions through the documented API states.
6. FFmpeg generates `playlist.m3u8` and media segments.
7. The browser plays the HLS result.
8. The browser shows source and result separately.
9. FFmpeg or manifest failures appear as `FAILURE`.
10. Every checkpoint branch passes its independent acceptance checklist.

## 13. Optional operational discussion

Discuss these after the core hands-on flow works; do not silently implement them as beginner requirements:

- Retry policy and duplicate execution.
- Idempotency and output replacement.
- Redis broker visibility and persistence tradeoffs.
- Worker concurrency and prefetch settings.
- Soft/hard task time limits.
- Persistent job-state storage.
- Upload and output cleanup policies.
- Request body limits at a reverse proxy.
- FFmpeg option tuning.
- WebM and variable-frame-rate FPS metadata.
- Monitoring, metrics, and alerts.
