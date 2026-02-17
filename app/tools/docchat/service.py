# app/tools/docchat/service.py

import base64
import mimetypes

import requests
from app.core.config import settings

# --- OpenCV preprocessing deps ---
import cv2
import numpy as np

MISTRAL_CHAT_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_OCR_URL = "https://api.mistral.ai/v1/ocr"


def _auth_headers() -> dict:
    api_key = settings.MISTRAL_API_KEY
    if not api_key:
        raise ValueError("MISTRAL_API_KEY is not set")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


# ----------------------------
# Image Preprocessing (OpenCV)
# ----------------------------
def preprocess_for_ocr(image_bytes: bytes) -> bytes:
    """
    Gentle preprocessing to improve OCR on phone pics / scans:
    - grayscale
    - CLAHE contrast
    - light denoise
    - light sharpen (unsharp mask)
    Returns PNG bytes.
    """
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image bytes")

    # 1) Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2) Contrast normalize (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # 3) Light denoise (keeps edges)
    gray = cv2.fastNlMeansDenoising(gray, h=10)

    # 4) Light sharpen (unsharp mask)
    blur = cv2.GaussianBlur(gray, (0, 0), sigmaX=1.0)
    sharp = cv2.addWeighted(gray, 1.5, blur, -0.5, 0)

    # Encode as PNG (best for OCR, lossless)
    ok, out = cv2.imencode(".png", sharp)
    if not ok:
        raise RuntimeError("Failed to encode processed image")
    return out.tobytes()


def mistral_chat(messages, model=None, temperature=0.2, max_tokens=800):
    """
    messages format:
    [
      {"role": "system", "content": "..."},
      {"role": "user", "content": "..."}
    ]
    """
    payload = {
        "model": model or settings.MISTRAL_CHAT_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    r = requests.post(MISTRAL_CHAT_URL, json=payload, headers=_auth_headers(), timeout=60)
    if not r.ok:
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise RuntimeError(f"Mistral Chat API error ({r.status_code}): {detail}")

    data = r.json()
    return data["choices"][0]["message"]["content"]


def mistral_ocr_to_markdown(file_bytes: bytes, filename: str, content_type: str | None = None):
    """
    Calls Mistral OCR model (mistral-ocr-2512) to extract Markdown.
    Returns: (pages_count, combined_markdown, raw_response_json)

    Behavior:
    - PDFs: sent as-is
    - Images: preprocessed via OpenCV, then sent as PNG for best OCR

    Expects OCR response: data["pages"][i]["markdown"]
    """
    # Determine mime
    ctype = (content_type or "").lower().strip()
    if not ctype:
        guessed, _ = mimetypes.guess_type(filename)
        ctype = guessed or "application/octet-stream"

    is_pdf = ctype == "application/pdf" or filename.lower().endswith(".pdf")
    is_img = ctype.startswith("image/") or filename.lower().endswith((".png", ".jpg", ".jpeg"))

    if not (is_pdf or is_img):
        raise ValueError("Only PDF or image files are allowed for OCR.")

    # Preprocess images (convert to clean PNG bytes)
    if is_img:
        file_bytes = preprocess_for_ocr(file_bytes)
        ctype = "image/png"
        filename = "preprocessed.png"

    # Build data URL
    b64 = base64.b64encode(file_bytes).decode("utf-8")

    if is_pdf:
        document = {"type": "document_url", "document_url": f"data:application/pdf;base64,{b64}"}
    else:
        document = {"type": "image_url", "image_url": f"data:{ctype};base64,{b64}"}

    payload = {
        "model": settings.MISTRAL_OCR_MODEL,  # should be mistral-ocr-2512
        "document": document,
        # optional OCR knobs can be added later here
    }

    r = requests.post(MISTRAL_OCR_URL, json=payload, headers=_auth_headers(), timeout=120)
    if not r.ok:
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise RuntimeError(f"Mistral OCR API error ({r.status_code}): {detail}")

    data = r.json()

    pages = data.get("pages") or []
    pages_count = len(pages) if pages else 0
    combined_md = "\n\n".join([(p.get("markdown") or "").strip() for p in pages]).strip()

    if not combined_md:
        combined_md = "(No text extracted.)"

    return pages_count, combined_md, data
