# app/tools/voicechat/service.py
"""
Voice Intelligence service layer.

- Transcription: Mistral Audio Transcriptions endpoint (Voxtral).
- LLM: Mistral Chat Completions (for Q&A + sentiment analysis).

Notes:
- For demo/MVP we return plain transcript text. Later you can store transcript server-side by audio_id.
- Voxtral endpoint supports options like diarize and timestamp granularities; keep minimal for now.
"""

import requests
from app.core.config import settings

MISTRAL_CHAT_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_AUDIO_TRANSCRIBE_URL = "https://api.mistral.ai/v1/audio/transcriptions"


def _auth_headers_json() -> dict:
    api_key = getattr(settings, "MISTRAL_API_KEY", None)
    if not api_key:
        raise ValueError("MISTRAL_API_KEY is not set")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _auth_headers_multipart() -> dict:
    api_key = getattr(settings, "MISTRAL_API_KEY", None)
    if not api_key:
        raise ValueError("MISTRAL_API_KEY is not set")
    # IMPORTANT: do NOT set Content-Type manually for multipart; requests will set boundary.
    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }


def mistral_chat(messages, model=None, temperature=0.2, max_tokens=800):
    """
    messages format:
    [
      {"role": "system", "content": "..."},
      {"role": "user", "content": "..."}
    ]
    """
    payload = {
        "model": model or getattr(settings, "MISTRAL_CHAT_MODEL", "mistral-small-latest"),
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    r = requests.post(MISTRAL_CHAT_URL, json=payload, headers=_auth_headers_json(), timeout=60)
    if not r.ok:
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise RuntimeError(f"Mistral Chat API error ({r.status_code}): {detail}")

    data = r.json()
    return data["choices"][0]["message"]["content"]


def voxtral_transcribe(
    audio_bytes: bytes,
    filename: str,
    content_type: str | None = None,
    language: str | None = None,
    diarize: bool = False,
    timestamps: list[str] | None = None,  # ["segment"] or ["word"]
):
    """
    Calls Mistral Audio Transcriptions endpoint using Voxtral model.

    Returns: (transcript_text, raw_response_json)

    Implementation uses multipart upload (file + params). This matches typical API behavior for audio STT.
    """
    model = getattr(settings, "MISTRAL_VOXTRAL_MODEL", None) or "voxtral-mini-latest"

    data = {"model": model}
    if language:
        data["language"] = language
    if diarize:
        data["diarize"] = "true"
    if timestamps:
        # API expects an array; multipart form can repeat the field or send JSON-ish string.
        # Keep it simple: send as JSON string.
        import json
        data["timestamp_granularities"] = json.dumps(timestamps)

    files = {
        "file": (filename or "audio", audio_bytes, content_type or "application/octet-stream")
    }

    r = requests.post(
        MISTRAL_AUDIO_TRANSCRIBE_URL,
        headers=_auth_headers_multipart(),
        data=data,
        files=files,
        timeout=180,
    )

    if not r.ok:
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise RuntimeError(f"Mistral Audio Transcription API error ({r.status_code}): {detail}")

    out = r.json()
    text = (out.get("text") or "").strip()
    if not text:
        text = "(No transcript returned.)"
    return text, out
