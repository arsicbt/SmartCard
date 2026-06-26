---
name: SmartCard architecture
description: How the two Flask apps wire together and the Replit run/deploy setup.
---

SmartCard is two separate Flask apps, not one:
- Backend (`Backend/app.py`): REST API, binds `127.0.0.1:8000` (env `BACKEND_PORT`). Calls `storage.reload()` at startup to create tables idempotently.
- Frontend (`Frontend/front.py`): server-rendered Jinja UI + proxy, binds `0.0.0.0:5000` (env `PORT`). Reaches the API via `BACKEND_URL` (default `http://localhost:8000`) + `/api`.

**Why:** Replit preview needs the user-facing app on port 5000; backend must not collide, so it lives on 8000.

DB: uses provisioned Postgres via `DATABASE_URL` secret (falls back to sqlite if unset). PG* secrets are present.

Groq: `Backend/Services/pdfAnalysisService.py` uses lazy `get_groq_client()` — app imports/runs without `GROQ_API_KEY`; only PDF→flashcard/quiz generation requires it.

Deploy: autoscale, single command runs backend gunicorn (127.0.0.1:8000) in background + frontend gunicorn (0.0.0.0:5000) foreground.
