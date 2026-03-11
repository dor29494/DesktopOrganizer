"""
Lightweight proxy server for Desktop Organizer.
Holds the API key server-side so end-users don't need their own.
Includes per-IP rate limiting.
"""

import os
import time
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)

# ── Config from environment variables ────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
RATE_LIMIT = int(os.environ.get("RATE_LIMIT", "10"))        # requests per window
RATE_WINDOW = int(os.environ.get("RATE_WINDOW", "3600"))     # window in seconds (1 hour)

# ── In-memory rate limiter (per IP) ──────────────────────────────────────────
_rate_store: dict[str, list[float]] = {}


def _is_rate_limited(ip: str) -> bool:
    now = time.time()
    timestamps = _rate_store.get(ip, [])
    # Remove expired entries
    timestamps = [t for t in timestamps if now - t < RATE_WINDOW]
    _rate_store[ip] = timestamps
    if len(timestamps) >= RATE_LIMIT:
        return True
    timestamps.append(now)
    return False


# ── AI call ──────────────────────────────────────────────────────────────────
def call_gemini(system_prompt: str, user_message: str) -> str:
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_message,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=2048,
        ),
    )
    return response.text


def parse_json_response(text: str) -> dict:
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


# ── Routes ───────────────────────────────────────────────────────────────────
@app.route("/api/organize", methods=["POST"])
def organize():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if _is_rate_limited(ip):
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429

    data = request.get_json()
    if not data or "system_prompt" not in data or "user_message" not in data:
        return jsonify({"error": "Missing system_prompt or user_message"}), 400

    try:
        raw = call_gemini(data["system_prompt"], data["user_message"])
        result = parse_json_response(raw)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
