This guide shows exact commands to push the current project to GitHub and deploy to Render.

1) Prepare your Git repo (run from repository root)

PowerShell (Windows):

```powershell
# initialize repo if needed
if (-not (Test-Path .git)) { git init }
# add remote (replace with your repo URL)
git remote remove origin -ErrorAction SilentlyContinue
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
# stage and commit
git add .
git commit -m "Add FastAPI app and deployment files"
# push (replace branch name if needed)
git push -u origin main
```

Bash (Linux/macOS):

```bash
[ -d .git ] || git init
git remote remove origin || true
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
git add .
git commit -m "Add FastAPI app and deployment files"
git push -u origin main
```

2) Render deployment (recommended)

- Sign in to Render at https://render.com
- Click "New" → "Web Service"
- Connect your GitHub account and select the repository and branch

Choose environment:
- If you want to use your `Dockerfile`: choose "Docker". Render will build and run the container.
- If you prefer Render to build from Python files: choose "Web Service (Python)" and set:
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `gunicorn -k uvicorn.workers.UvicornWorker fastapi_app:app --bind 0.0.0.0:$PORT --workers 2`

Environment variables (Render dashboard → Environment):
- `GOLDAPI_KEY` = your GoldAPI API key

Deployment options:
- Instance type: start with the free / smallest plan for testing
- Health check path: optional `/health` if you add that route

3) Post-deploy
- Open the service URL from Render dashboard to test `/api/gold-rates`
- Check Logs in Render for any build/runtime errors

4) Local testing

```bash
pip install -r requirements.txt
uvicorn fastapi_app:app --reload --host 0.0.0.0 --port 8000
```

5) If you want me to create a Git commit patch instead of pushing, tell me the GitHub repo URL and I will prepare a patch file you can apply.
