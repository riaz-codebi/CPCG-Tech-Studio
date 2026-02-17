# app/tools/bi/router.py

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from .service import get_bi_reports, get_categories

router = APIRouter()


@router.get("/tools/bi", response_class=HTMLResponse)
async def bi_portfolio(request: Request):
    reports = get_bi_reports()
    categories = get_categories(reports)

    # If your Document Intelligence uses request.state.user, keep it consistent:
    user = getattr(request.state, "user", None)

    return request.app.state.templates.TemplateResponse(
        "bi_portfolio.html",  # you said it lives in app/templates/bi_portfolio.html
        {
            "request": request,
            "title": "Business Intelligence",
            "active_page": "bi",   # your base.html uses this for active nav highlighting
            "user": user,
            "reports": reports,
            "categories": categories,
        },
    )
