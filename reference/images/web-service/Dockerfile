# Builder stage
FROM ghcr.io/astral-sh/uv:python3.14-alpine AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODY=copy

WORKDIR /app

COPY . /app

RUN uv sync --frozen --no-dev --no-editable

# Final stage
FROM python:3.14-alpine

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"
ENV PORT=8000
ENV VISIT_COUNTER_FILE="/var/lib/web-service/visits.txt"
ENV OLLAMA_URL="http://localhost:11434"
ENV OLLAMA_MODEL="qwen3:0.6b"

CMD ["sh", "-c", "gunicorn web_service:app --bind 0.0.0.0:$PORT --timeout 120"]