# app/tools/voicechat/router.py

import uuid
from typing import Optional

from fastapi import APIRouter, Body, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.tools.voicechat.service import mistral_chat, voxtral_transcribe

router = APIRouter()

# Templates live under app/templates (per your structure)
templates = Jinja2Templates(directory="app/templates")

# Basic allowlist; expand later if needed
ALLOWED_EXT = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".webm"}
ALLOWED_MIME_PREFIX = ("audio/",)


def _ext(name: Optional[str]) -> str:
    name = (name or "").lower().strip()
    dot = name.rfind(".")
    return name[dot:] if dot >= 0 else ""


def _is_allowed_upload(file: UploadFile) -> bool:
    ext = _ext(file.filename)
    ctype = (file.content_type or "").lower()
    if ext in ALLOWED_EXT:
        return True
    if any(ctype.startswith(p) for p in ALLOWED_MIME_PREFIX):
        return True
    return False


@router.get("/tools/voice", response_class=HTMLResponse)
async def voice_intelligence_page(request: Request):
    """
    Renders the Voice Intelligence landing page.
    Sidebar in base_auth.html links to /tools/voice.
    """
    user = getattr(request.state, "user", None)

    return templates.TemplateResponse(
        "voice_intelligence.html",
        {
            "request": request,
            "user": user,
            "active_page": "voice",
            "page_title": "Voice Intelligence",
        },
    )


@router.post("/api/voice/upload")
async def voice_upload(file: UploadFile = File(...)):
    """
    Upload endpoint for the Voice Intelligence modal.
    Returns: audio_id, transcript (REAL STT via Voxtral)
    """
    if not _is_allowed_upload(file):
        raise HTTPException(status_code=400, detail="Only audio files are allowed.")

    raw = await file.read()
    audio_id = str(uuid.uuid4())

    try:
        transcript, _raw_json = voxtral_transcribe(
            audio_bytes=raw,
            filename=file.filename or "audio",
            content_type=file.content_type,
            # Optional knobs you can enable later:
            # language="en",
            diarize=False,
            timestamps=None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse({"audio_id": audio_id, "transcript": transcript})


@router.post("/api/voice/clear/{audio_id}")
async def voice_clear(audio_id: str):
    """
    Called when user clicks 'Close and clear audio'.
    Stub for now. Later: delete temp objects / cached transcript keyed by audio_id.
    """
    return JSONResponse({"ok": True, "audio_id": audio_id})


@router.post("/api/voice/query")
async def voice_query(payload: dict = Body(...)):
    """
    payload:
    {
      "audio_id": "...",
      "question": "...",
      "transcript": "..."   # MVP: transcript passed from client; later load by audio_id server-side
    }
    """
    question = (payload.get("question") or "").strip()
    transcript = (payload.get("transcript") or "").strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question is required.")
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript content is missing.")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a voice intelligence assistant. "
                "Answer using only the transcript content. "
                "If the answer is not in the transcript, say you cannot find it."
            ),
        },
        {"role": "user", "content": f"TRANSCRIPT:\n\n{transcript}\n\nQUESTION:\n{question}"},
    ]

    try:
        answer = mistral_chat(messages=messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse({"answer": answer})


@router.post("/api/voice/sentiment")
async def voice_sentiment(payload: dict = Body(...)):
    """
    payload:
    {
      "audio_id": "...",
      "transcript": "...",
      "prompt": "..."   # optional override; UI sends a robust default prompt
    }
    """
    transcript = (payload.get("transcript") or "").strip()
    prompt = (payload.get("prompt") or "").strip()

    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript content is missing.")

    if not prompt:
        prompt = (
            "Analyze the transcript for sentiment and safety signals. "
            "Provide: overall sentiment, tone progression, emotions, escalation, abusive language, risk flags, "
            "and an actionable summary. Use only evidence from the transcript."
        )

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert conversation analyst. "
                "Stay grounded in the transcript; do not invent details."
            ),
        },
        {"role": "user", "content": f"{prompt}\n\nTRANSCRIPT:\n\n{transcript}"},
    ]

    try:
        analysis = mistral_chat(messages=messages, temperature=0.2, max_tokens=900)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse({"analysis": analysis})
