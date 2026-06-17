<#
Usage:
  Open PowerShell in the project root and run:

  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\deploy_and_render.ps1 -RepoUrl "https://github.com/MachineLearnerSatyam/Gold_Live-_Rate.git"

Notes:
- This script will commit local changes and push to the provided remote. It uses your local Git credentials (Windows credential manager or SSH agent).
- I cannot push on your behalf; run this script locally so your credentials are used.
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$RepoUrl,
    [string]$Branch = "main",
    [string]$CommitMessage = "Add deployment files and read GOLDAPI_KEY from env"
)

function Run($cmd) {
    Write-Host "> $cmd"
    & cmd /c $cmd
    if ($LASTEXITCODE -ne 0) { throw "Command failed: $cmd" }
}

# Ensure git initialized
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git repository..."
    Run "git init"
}

# Set remote
try {
    Run "git remote remove origin"
} catch { }
Run "git remote add origin $RepoUrl"

# Commit & push
Run "git add ."
# Allow empty commits to avoid error if nothing changed
Run "git commit -m \"$CommitMessage\" || echo 'No changes to commit'"
Run "git push -u origin $Branch"

Write-Host "\nRepository pushed.\nNext: Create a Render Web Service. Follow these steps:" -ForegroundColor Green
Write-Host "1) Sign in to https://render.com and click 'New' → 'Web Service'"
Write-Host "2) Connect your GitHub account and select the repository and branch you just pushed"
Write-Host "3) For Environment choose 'Docker' (recommended) or 'Web Service (Python)'."
Write-Host "   - If Docker: Render will build the provided Dockerfile automatically."
Write-Host "   - If Python: set Build command: 'pip install -r requirements.txt' and Start command: 'gunicorn -k uvicorn.workers.UvicornWorker fastapi_app:app --bind 0.0.0.0:$PORT --workers 2'"
Write-Host "4) In Render dashboard -> Environment, add: GOLDAPI_KEY = <your_goldapi_key>"
Write-Host "5) Create the service and wait for the build to finish. Open /api/gold-rates to verify."

Write-Host "\nIf you want, share the Render service URL and I can validate the API endpoint for you." -ForegroundColor Cyan
