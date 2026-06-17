Deploying to Render (quick guide)

1) Push your repo to GitHub

2) In Render:
   - Create -> Web Service
   - Connect GitHub and select this repository and branch
   - Environment: `Docker` or `Static Site` (choose `Docker` if you want to use the included `Dockerfile`, otherwise choose `Python`)

If using Docker (recommended):
   - Render will build the provided `Dockerfile` automatically.

If using the Python (build from repo) option:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn -k uvicorn.workers.UvicornWorker fastapi_app:app --bind 0.0.0.0:$PORT --workers 2`

3) Environment variables
   - Set `GOLDAPI_KEY` to your GoldAPI key in Render dashboard (Settings -> Environment).

4) Health check (optional)
   - Add a simple route `/health` returning 200 if you want Render to use it as a health check.

5) Local testing
   - Run locally with:

```bash
uvicorn fastapi_app:app --reload --host 0.0.0.0 --port 8000
```

6) Notes
   - Updated `fastapi_app.py` now reads `GOLDAPI_KEY` from env; the previous hardcoded key is kept as a fallback.
   - After deploy, open the service URL in the Render dashboard.
