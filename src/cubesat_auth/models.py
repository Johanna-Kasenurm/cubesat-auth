from datetime import datetime, timedelta, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cubesat_auth.config import TOKEN_EXPIRY_HOURS
from cubesat_auth.db import Base


# Create the users table
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="User")
    created_at: Mapped[datetime] = mapped_column(DateTime, default= lambda:datetime.now(timezone.utc))

    # One user can have many sessions
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan") # cascade to delete all sessions when the user is deleted


# Create the sessions table
class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    # One session belongs to one user
    user = relationship("User", back_populates="sessions") # each session belongs to a single user