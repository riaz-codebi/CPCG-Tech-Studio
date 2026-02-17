from fastapi import Request
from fastapi.responses import RedirectResponse

def get_current_user(request: Request):
    return request.session.get("user")

def require_login(request: Request):
    if not get_current_user(request):
        return RedirectResponse(url="/", status_code=302)
    return None
