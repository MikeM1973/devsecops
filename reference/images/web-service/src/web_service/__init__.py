import fcntl
import os
from pathlib import Path

import ollama
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

COUNTER_FILE = Path(
    os.environ.get("VISIT_COUNTER_FILE", "/var/lib/web-service/visits.txt")
)
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:0.6b")


def increment_visits() -> int:
    COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(COUNTER_FILE, "a+", encoding="utf-8") as f:
        # Lock so concurrent workers cannot interleave read/write.
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            contents = f.read().strip()
            try:
                count = int(contents)
            except ValueError:
                count = 0
            count += 1
            f.seek(0)
            f.truncate()
            f.write(str(count))
            f.flush()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    return count


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
