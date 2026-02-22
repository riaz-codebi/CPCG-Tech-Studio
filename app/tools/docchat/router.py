# app/tools/docchat/router.py

import uuid
from typing import Optional

from fastapi import APIRouter, Body, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.tools.docchat.service import mistral_chat, mistral_ocr_to_markdown

router = APIRouter()

# Templates live under app/templates (per your structure)
templates = Jinja2Templates(directory="app/templates")

ALLOWED_EXT = {".pdf", ".png", ".jpg", ".jpeg"}
ALLOWED_MIME_EXACT = {"application/pdf"}
ALLOWED_MIME_PREFIX = ("image/",)


def _ext(name: Optional[str]) -> str:
    name = (name or "").lower().strip()
    dot = name.rfind(".")
    return name[dot:] if dot >= 0 else ""


def _is_allowed_upload(file: UploadFile) -> bool:
    ext = _ext(file.filename)
    ctype = (file.content_type or "").lower()

    if ext in ALLOWED_EXT:
        return True
    if ctype in ALLOWED_MIME_EXACT:
        return True
    if any(ctype.startswith(p) for p in ALLOWED_MIME_PREFIX):
        return True
    return False


@router.get("/tools/docchat", response_class=HTMLResponse)
async def doc_intelligence_page(request: Request):
    """
    Renders the Document Intelligence landing page.
    Sidebar in base_auth.html already links to /tools/docchat.
    """
    user = getattr(request.state, "user", None)

    return templates.TemplateResponse(
        "doc_intelligence.html",
        {
            "request": request,
            "user": user,
            "active_page": "docchat",
            "page_title": "Document Intelligence",
        },
    )


@router.post("/api/docchat/upload")
async def docchat_upload(file: UploadFile = File(...)):
    """
    Upload endpoint for the modal.
    Returns: doc_id, pages, markdown (REAL OCR via Mistral OCR model)
    """
    if not _is_allowed_upload(file):
        raise HTTPException(status_code=400, detail="Only PDF or image files are allowed.")

    raw = await file.read()
    doc_id = str(uuid.uuid4())

    try:
        # Run Mistral OCR (mistral-ocr-2512) -> markdown
        pages, markdown, _raw_json = mistral_ocr_to_markdown(
            file_bytes=raw,
            filename=file.filename or "upload",
            content_type=file.content_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse({"doc_id": doc_id, "pages": pages, "markdown": markdown})



@router.post("/api/docchat/upload_clipboard")
async def docchat_upload_clipboard(files: list[UploadFile] = File(...)):
    """
    Accepts multiple screenshot images from clipboard capture flow.
    Combines OCR markdown from all images into one document (in order sent).
    Returns: doc_id, pages, markdown
    """
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="At least one image is required.")

    # Validate all are images
    for f in files:
        ctype = (f.content_type or "").lower()
        if not (ctype.startswith("image/") or _ext(f.filename) in {".png", ".jpg", ".jpeg"}):
            raise HTTPException(status_code=400, detail="Only image files are allowed for on-screen capture.")

    doc_id = str(uuid.uuid4())

    total_pages = 0
    md_parts: list[str] = []

    try:
        for idx, f in enumerate(files, start=1):
            raw = await f.read()
            pages, markdown, _raw_json = mistral_ocr_to_markdown(
                file_bytes=raw,
                filename=f.filename or f"snip_{idx}.png",
                content_type=f.content_type,
            )
            total_pages += max(pages, 1)
            if markdown:
                md_parts.append(f"\n\n---\n\n# Screenshot {idx}\n\n{markdown.strip()}\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    combined = "\n".join(md_parts).strip() or "(No text extracted.)"

    return JSONResponse({"doc_id": doc_id, "pages": total_pages, "markdown": combined})



@router.post("/api/docchat/clear/{doc_id}")
async def docchat_clear(doc_id: str):
    """
    Called when user clicks 'Close and clear document'.
    Stub for now. Later: delete temp objects / cached OCR output keyed by doc_id.
    """
    return JSONResponse({"ok": True, "doc_id": doc_id})


@router.post("/api/docchat/query")
async def docchat_query(payload: dict = Body(...)):
    """
    payload:
    {
      "doc_id": "...",
      "question": "...",
      "markdown": "..."   # MVP: markdown passed from client; later load by doc_id server-side
    }
    """
    question = (payload.get("question") or "").strip()
    markdown = (payload.get("markdown") or "").strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question is required.")
    if not markdown:
        raise HTTPException(status_code=400, detail="Document content is missing.")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a document intelligence assistant. "
                "Answer using only the document content. "
                "If the answer is not in the document, say you cannot find it."
            ),
        },
        {"role": "user", "content": f"DOCUMENT:\n\n{markdown}\n\nQUESTION:\n{question}"},
    ]

    try:
        answer = mistral_chat(messages=messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse({"answer": answer})
