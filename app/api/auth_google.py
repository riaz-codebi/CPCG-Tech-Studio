from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth

from app.core.config import settings
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.models.deps import get_db
from app.db.models.identity import upsert_google_user

router = APIRouter(prefix="/auth/google", tags=["auth"])

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/login")
async def google_login(request: Request):
    # Redirect user to Google
    return await oauth.google.authorize_redirect(request, settings.GOOGLE_REDIRECT_URI)

"""
@router.get("/callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)

    # ✅ Get user profile from Google userinfo endpoint (no id_token needed)
    resp = await oauth.google.get("https://openidconnect.googleapis.com/v1/userinfo", token=token)
    user = resp.json()

    request.session["user"] = {
        "sub": user.get("sub"),
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture"),
    }

    return RedirectResponse(url="/studio", status_code=302)
"""
@router.get("/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)

    # Get profile
    resp = await oauth.google.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        token=token
    )
    profile = resp.json()

    # ✅ Save or update user in Postgres
    db_user = upsert_google_user(db, profile)

    # ✅ Store session
    request.session["user"] = {
        "id": db_user.id,
        "sub": profile.get("sub"),
        "email": db_user.email,
        "name": db_user.full_name,
        "picture": db_user.picture_url,
    }

    return RedirectResponse(url="/studio", status_code=302)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)
