# Builder stage
FROM ghcr.io/astral-sh/uv:python3.14-alpine AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY . /app

RUN uv sync --frozen --no-dev --no-editable

# Final stage
FROM python:3.14-alpine

ARG USER_UID=1000
ARG USER_GID=1000
RUN addgroup -g $USER_GID -S appuser && adduser -u $USER_UID -S appuser -G appuser

WORKDIR /app

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"
ENV PORT=8000
ENV VISIT_COUNTER_FILE="/var/lib/web-service/visits.txt"
ENV OLLAMA_URL="http://localhost:11434"
ENV OLLAMA_MODEL="qwen3:0.6b"

RUN mkdir $(dirname $VISIT_COUNTER_FILE) && \
    chown appuser:appuser $(dirname $VISIT_COUNTER_FILE)

USER appuser

CMD ["sh", "-c", "gunicorn web_service:app --bind 0.0.0.0:$PORT --timeout 120"]
