import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SearchResult(Base):
    __tablename__ = "search_results"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    search_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("searches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Raw data from the web search API
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_position: Mapped[int] = mapped_column(Integer, nullable=False)

    # Produced by Agent 2 (relevance scoring)
    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    relevance_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # User actions
    is_starred: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_recruited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    search: Mapped["Search"] = relationship(back_populates="results")  # noqa: F821
