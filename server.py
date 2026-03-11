"""
Lightweight proxy server for Desktop Organizer.
Holds the API keys server-side so end-users don't need their own.
Uses Claude first (daily limit), then falls back to Gemini.
Includes per-IP rate limiting.
"""

import os
import time
import json
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── Config from environment variables ────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
CLAUDE_DAILY_LIMIT = int(os.environ.get("CLAUDE_DAILY_LIMIT", "25"))
RATE_LIMIT = int(os.environ.get("RATE_LIMIT", "10"))        # requests per IP per window
RATE_WINDOW = int(os.environ.get("RATE_WINDOW", "3600"))     # window in seconds (1 hour)

# ── Claude daily usage counter ───────────────────────────────────────────────
_claude_usage = {"date": "", "count": 0}


def _get_claude_usage() -> int:
    """Return how many Claude calls have been made today. Resets at midnight UTC."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if _claude_usage["date"] != today:
        _claude_usage["date"] = today
        _claude_usage["count"] = 0
    return _claude_usage["count"]


def _increment_claude_usage():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if _claude_usage["date"] != today:
        _claude_usage["date"] = today
        _claude_usage["count"] = 0
    _claude_usage["count"] += 1


def _is_claude_available() -> bool:
    return bool(ANTHROPIC_API_KEY) and _get_claude_usage() < CLAUDE_DAILY_LIMIT


# ── In-memory rate limiter (per IP) ──────────────────────────────────────────
_rate_store: dict[str, list[float]] = {}


def _is_rate_limited(ip: str) -> bool:
    now = time.time()
    timestamps = _rate_store.get(ip, [])
    timestamps = [t for t in timestamps if now - t < RATE_WINDOW]
    _rate_store[ip] = timestamps
    if len(timestamps) >= RATE_LIMIT:
        return True
    timestamps.append(now)
    return False


# ── AI calls ─────────────────────────────────────────────────────────────────
def call_claude(system_prompt: str, user_message: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


def call_gemini(system_prompt: str, user_message: str) -> str:
    from google import genai
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

    used_provider = "claude"
    fallback = False

    try:
        if _is_claude_available():
            raw = call_claude(data["system_prompt"], data["user_message"])
            _increment_claude_usage()
        else:
            used_provider = "gemini"
            fallback = True
            raw = call_gemini(data["system_prompt"], data["user_message"])

        result = parse_json_response(raw)
        return jsonify({
            **result,
            "_meta": {
                "provider": used_provider,
                "fallback": fallback,
                "claude_remaining": max(0, CLAUDE_DAILY_LIMIT - _get_claude_usage()),
            },
        })
    except Exception as e:
        # If Claude fails, try Gemini as fallback
        if used_provider == "claude":
            try:
                raw = call_gemini(data["system_prompt"], data["user_message"])
                result = parse_json_response(raw)
                return jsonify({
                    **result,
                    "_meta": {
                        "provider": "gemini",
                        "fallback": True,
                        "claude_remaining": max(0, CLAUDE_DAILY_LIMIT - _get_claude_usage()),
                    },
                })
            except Exception as e2:
                return jsonify({"error": str(e2)}), 500
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "claude_remaining": max(0, CLAUDE_DAILY_LIMIT - _get_claude_usage()),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
