import fcntl
import os
from pathlib import Path
from urllib.parse import urlparse

import ollama
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Either a local filesystem path or an s3://bucket/key URL.
COUNTER_FILE = os.environ.get("VISIT_COUNTER_FILE", "/var/lib/web-service/visits.txt")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:0.6b")

S3_MAX_ATTEMPTS = 10


def _parse_count(contents: str) -> int:
    try:
        return int(contents.strip())
    except ValueError:
        return 0


def increment_visits_local(path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a+", encoding="utf-8") as f:
        # Lock so concurrent workers cannot interleave read/write.
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            count = _parse_count(f.read()) + 1
            f.seek(0)
            f.truncate()
            f.write(str(count))
            f.flush()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    return count


def increment_visits_s3(url: str) -> int:
    import boto3
    from botocore.exceptions import ClientError

    parsed = urlparse(url)
    bucket, key = parsed.netloc, parsed.path.lstrip("/")
    client = boto3.client("s3")

    # S3 has no locking, so use conditional writes and retry on conflict.
    for _ in range(S3_MAX_ATTEMPTS):
        try:
            response = client.get_object(Bucket=bucket, Key=key)
        except ClientError as exc:
            if exc.response["Error"]["Code"] not in ("NoSuchKey", "404"):
                raise
            count = 1
            condition = {"IfNoneMatch": "*"}
        else:
            count = _parse_count(response["Body"].read().decode("utf-8")) + 1
            condition = {"IfMatch": response["ETag"]}

        try:
            client.put_object(
                Bucket=bucket, Key=key, Body=str(count).encode("utf-8"), **condition
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] not in (
                "PreconditionFailed",
                "ConditionalRequestConflict",
            ):
                raise
        else:
            return count

    raise RuntimeError(f"Could not update visit counter at {url} after contention")


def increment_visits() -> int:
    if urlparse(COUNTER_FILE).scheme == "s3":
        return increment_visits_s3(COUNTER_FILE)
    return increment_visits_local(Path(COUNTER_FILE))


@app.route("/")
def index() -> str:
    return render_template("index.html", visits=increment_visits())


@app.route("/api/visits")
def api_visits():
    return jsonify(visits=increment_visits())


@app.route("/api/status")
def api_status():
    ollama_status = {"url": OLLAMA_URL, "model": OLLAMA_MODEL}
    try:
        models = [m.model for m in ollama.Client(host=OLLAMA_URL).list().models]
    except Exception as exc:
        ollama_status["status"] = "unavailable"
        ollama_status["error"] = str(exc)
    else:
        ollama_status["status"] = "ok"
        ollama_status["models"] = models
        ollama_status["model_available"] = OLLAMA_MODEL in models

    return jsonify(status="ok", ollama=ollama_status)


@app.route("/chat", methods=["POST"])
def chat() -> str:
    prompt = request.form.get("prompt", "").strip()
    if not prompt:
        return render_template(
            "chat.html", prompt=prompt, thinking=None, response="No message provided."
        )

    client = ollama.Client(host=OLLAMA_URL)
    reply = client.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        think=True,
    )
    return render_template(
        "chat.html",
        prompt=prompt,
        thinking=reply.message.thinking,
        response=reply.message.content,
    )


def main() -> None:
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
