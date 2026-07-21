# Checkpoint Acceptance Checklist

Use this document when creating or reviewing checkpoint branches. Each branch must be checked out in a clean working tree and started independently.

## Shared rules for every checkpoint

- [ ] The branch contains no references to later checkpoint files or behavior.
- [ ] `docker compose config` succeeds.
- [ ] The documented startup command matches the branch.
- [ ] Service names, ports, environment variables, and volume paths are internally consistent.
- [ ] The README or workshop notes state one clear expected result.
- [ ] A participant can continue without knowing concepts from a later checkpoint.

## `checkpoint/00-fastapi-setup`

Expected concept: bringing up a minimal FastAPI app and confirming the toolchain.

- [ ] FastAPI starts through Docker Compose.
- [ ] The static tutorial page is reachable.
- [ ] `GET /api/health` returns `{"status":"ok"}`.
- [ ] Swagger UI is reachable at `/docs`.
- [ ] The participant flow does not require upload, Redis, Celery, or FFmpeg.

Suggested verification:

```bash
curl -s http://localhost:8000/api/health
```

## `checkpoint/01-fastapi-upload`

Expected concept: receiving and storing a video through FastAPI.

- [ ] FastAPI starts through Docker Compose.
- [ ] The static tutorial page is reachable.
- [ ] Input and output directories are mounted or created consistently.
- [ ] `POST /api/videos` accepts a supported file.
- [ ] The upload is stored under a generated UUID job directory.
- [ ] Empty and unsupported files are rejected.
- [ ] The success response identifies the stored job.
- [ ] The participant flow does not require Redis, Celery, or FFmpeg.

Suggested verification:

```bash
curl -i -F "file=@samples/sample.mp4" http://localhost:8000/api/videos
```

## `checkpoint/02-celery-redis`

Expected concept: enqueueing work and observing asynchronous state.

- [ ] Redis starts.
- [ ] The Celery worker starts and connects to Redis.
- [ ] The API can enqueue a simple teaching task.
- [ ] Job creation returns without waiting for the task.
- [ ] `GET /api/jobs/{job_id}` returns a documented public state.
- [ ] Unknown job IDs return `404`.
- [ ] The participant can see worker receipt/execution in logs.
- [ ] Real FFmpeg output is not required yet.

Suggested verification:

```bash
curl -s -F "file=@samples/sample.mp4" http://localhost:8000/api/videos
curl -s http://localhost:8000/api/jobs/<job_id>
```

## `checkpoint/03-ffmpeg-hls`

Expected concept: executing FFmpeg in the worker and propagating success/failure.

- [ ] The API process never launches FFmpeg.
- [ ] The worker reads the shared source file.
- [ ] Output is isolated under `data/outputs/{job_id}`.
- [ ] `playlist.m3u8` and at least one segment are generated.
- [ ] The status API returns `hls_url` only after success.
- [ ] FFmpeg non-zero exit produces `FAILURE`.
- [ ] Missing manifest produces `FAILURE`.
- [ ] Worker logs retain useful FFmpeg diagnostics.

Suggested verification:

```bash
find data/outputs/<job_id> -maxdepth 1 -type f -print
curl -s http://localhost:8000/api/jobs/<job_id>
```

## `checkpoint/04-hls-player`

Expected concept: polling an asynchronous job and consuming its result.

Workshop note: participants should use the provided `static/` from this branch (or GitHub), not hand-write the HLS player UI.
Repo: https://github.com/DSeung001/pycon-2026-fastapi-celery-tutorial/tree/checkpoint/04-hls-player/static

- [ ] The browser starts one polling loop for the active job.
- [ ] Polling stops on both `SUCCESS` and `FAILURE`.
- [ ] A new job does not leave the old polling timer active.
- [ ] The source player uses `source_url` from the API.
- [ ] The result player initializes only after success.
- [ ] Native HLS is used when available.
- [ ] hls.js is used as fallback.
- [ ] Previous hls.js instances are destroyed before reuse.
- [ ] Source and encoded result are labeled and visible separately.
- [ ] Encoding, network, and playback failures leave the UI in a stable state.

Suggested verification:

1. Open the tutorial page.
2. Create or enter a valid job.
3. Observe pending/started state.
4. Confirm polling stops at success.
5. Play both source and HLS result.
6. Repeat with a deliberately invalid source and confirm failure UI.
