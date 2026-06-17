FROM python:3.11-slim

WORKDIR /app

# Install system deps for httpx (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --no-cache-dir -r /app/requirements.txt

ENV PORT=8080
EXPOSE 8080

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "fastapi_app:app", "--bind", "0.0.0.0:8080", "--workers", "2"]
