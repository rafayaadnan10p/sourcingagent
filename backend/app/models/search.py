import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

PLATFORM_CHOICES = ("all", "linkedin", "github", "upwork", "fiverr", "behance")


class Search(Base):
    __tablename__ = "searches"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    jd_text: Mapped[str] = mapped_column(Text, nullable=False)
    jd_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Stored as a JSON array of search string objects produced by Agent 1
    search_strings: Mapped[Any] = mapped_column(JSONB, nullable=True)
    platform_scope: Mapped[str] = mapped_column(
        String(20), nullable=False, default="all"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="searches")  # noqa: F821
    results: Mapped[list["SearchResult"]] = relationship(  # noqa: F821
        back_populates="search", cascade="all, delete-orphan"
    )
