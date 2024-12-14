# Stage 1: Build Stage
FROM python:3.10-slim AS builder

WORKDIR /app

COPY . /app

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime Stage
FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

ENV PATH="/opt/venv/bin:$PATH"

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y tzdata apt-utils && \
    ln -snf /usr/share/zoneinfo/America/Phoenix /etc/localtime && \
    echo "America/Phoenix" > /etc/timezone && \
    apt-get clean

RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

EXPOSE 8086

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8086
ENV TZ=America/Phoenix

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://0.0.0.0:8086/ || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8086", "app:app"]