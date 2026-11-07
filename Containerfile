FROM docker.io/library/debian:trixie-slim
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv \
    libportaudio2 libsndfile1 libgomp1 ca-certificates tzdata && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.lock.txt /app/requirements.lock.txt
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --only-binary=:all: \
    -r /app/requirements.lock.txt && /opt/venv/bin/pip check
COPY --chown=1000:1000 runtime.py storage.py /app/
COPY --chown=1000:1000 recorder /app/recorder
COPY --chown=1000:1000 detector /app/detector
COPY --chown=1000:1000 webapp /app/webapp
ENV PATH=/opt/venv/bin:$PATH DB_PATH=/data/db/detections.sqlite3 \
    DETECTIONS_DIR=/data/detections LOG_DIR=/data/logs INCOMING_DIR=/audio/incoming \
    OUTPUT_DIR=/audio/incoming STATUS_DIR=/status COOLDOWN_STATE=/data/.cooldown \
    MPLCONFIGDIR=/tmp/matplotlib NUMBA_CACHE_DIR=/tmp/numba TZ=Europe/Amsterdam
USER 1000:1000
CMD ["python", "-m", "gunicorn", "--workers", "1", "--threads", "2", "--bind", "0.0.0.0:8090", "--chdir", "webapp", "app:app"]
