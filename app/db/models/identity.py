from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class AppUser(Base):
    __tablename__ = "app_users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    auth_provider: Mapped[str] = mapped_column(String, nullable=False, default="google")
    provider_user_id: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    full_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    picture_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("auth_provider", "provider_user_id", name="uq_app_users_provider"),
    )


from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models.identity import AppUser

def upsert_google_user(db: Session, profile: dict) -> AppUser:
    email = (profile.get("email") or "").lower().strip()
    sub = str(profile.get("sub") or "").strip()

    if not email or not sub:
        raise ValueError("Google profile missing email or sub")

    user = db.query(AppUser).filter(AppUser.email == email).first()

    now = datetime.utcnow()

    if user is None:
        user = AppUser(
            auth_provider="google",
            provider_user_id=sub,
            email=email,
            full_name=profile.get("name"),
            picture_url=profile.get("picture"),
            last_login_at=now,
            created_at=now,
            updated_at=now,
        )
        db.add(user)
    else:
        user.full_name = profile.get("name") or user.full_name
        user.picture_url = profile.get("picture") or user.picture_url
        user.provider_user_id = user.provider_user_id or sub
        user.last_login_at = now
        user.updated_at = now

    db.commit()
    db.refresh(user)
    return user
