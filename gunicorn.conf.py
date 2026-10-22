"""Gunicorn settings for the Docker image: async Uvicorn workers serving FastAPI."""

bind = "0.0.0.0:8000"
worker_class = "uvicorn.workers.UvicornWorker"
# Restart workers now and then (staggered) so memory can't creep up forever.
max_requests = 2000
max_requests_jitter = 400
timeout = 300
