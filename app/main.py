from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.api.auth_google import router as google_auth_router
from app.web.router import router as web_router
from app.tools.docchat.router import router as docchat_router
from app.tools.voicechat.router import router as voicechat_router
from app.tools.bi.router import router as bi_router

from app.db.session import engine
from app.db.base import Base

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.session import engine
from app.db.base import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown (optional)
    # engine.dispose()  # usually not necessary

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

#app = FastAPI(title=settings.APP_NAME)



# Session cookie (required for OAuth state + login session)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    same_site="lax",
    https_only=False,  # set True in prod with HTTPS
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")
app.state.templates = templates   # ✅ ADD THIS LINE

# Routers
app.include_router(google_auth_router)
app.include_router(web_router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "app_name": settings.APP_NAME},
    )

app.include_router(docchat_router)
app.include_router(voicechat_router)
app.include_router(bi_router)
