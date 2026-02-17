from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.security import require_login, get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/studio", response_class=HTMLResponse)
async def studio(request: Request):
    guard = require_login(request)
    if guard:
        return guard

    user = get_current_user(request)
    return templates.TemplateResponse(
        "studio.html",
        {
            "request": request,
            "user": user,
            "page_title": "Studio Home",
            "title": "CPCG Tech Studio"
    }
    )

