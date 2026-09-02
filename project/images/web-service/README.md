# web-service

A small Flask app that tracks visitors and forwards one-shot chat prompts to an
Ollama server.

## Endpoints

| Route | Method | Description |
| --- | --- | --- |
| `/` | GET | Renders `index.html` with the visitor count and a chat prompt box. |
| `/api/visits` | GET | Returns `{"visits": N}` as JSON. |
| `/api/status` | GET | Reports this server's status plus the Ollama server's reachability and available models. Always returns 200; check the `ollama.status` field. |
| `/chat` | POST | Sends the `prompt` form field to Ollama and renders the thinking and response on `chat.html`. The page is a dead end with a link back to `/`. |

Every request to `/` and `/api/visits` increments the persisted visitor count.

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `VISIT_COUNTER_FILE` | `/var/lib/web-service/visits.txt` | File holding the visitor count. The parent directory is created if needed. |
| `OLLAMA_URL` | `http://localhost:11434` | Base URL of the Ollama server. |
| `OLLAMA_MODEL` | `qwen3:0.6b` | Model used for chat requests. |
| `PORT` | `8000` | Port used by the built-in dev server (`web-service` script). |

## Files

- `src/web_service/__init__.py` — application and routes; `app` is the WSGI entry point.
- `src/web_service/templates/index.html`, `chat.html` — page templates.
- `src/web_service/templates/customize.html` — optional. If present, it is
  included at the top of the body on both pages, allowing deployments to inject
  a banner or other markup without changing the app.
- `visits.txt` (path from `VISIT_COUNTER_FILE`) — plain text file containing the
  current count. Access is guarded with an exclusive `flock`, so multiple
  workers can share it.

## Running

Dev server:

```
uv run web-service
```

Production:

```
uv run gunicorn web_service:app --bind 0.0.0.0:8000 --timeout 120
```
