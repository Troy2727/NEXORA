# NEXORA API image: Python 3.11, runtime dependencies from requirements.txt,
# runs as an unprivileged user. docker-compose starts it via entrypoint.sh.
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chmod=755 entrypoint.sh /usr/local/bin/nexora-entrypoint
COPY . .

RUN useradd --system --no-create-home --shell /usr/sbin/nologin nexora \
    && chown -R nexora:nexora /app
USER nexora

EXPOSE 8000
ENTRYPOINT ["nexora-entrypoint"]
CMD ["gunicorn", "main:app"]
