import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel


class SearchResultOut(BaseModel):
    id: uuid.UUID
    url: str
    title: str | None
    snippet: str | None
    original_position: int
    relevance_score: float | None
    relevance_reasoning: str | None
    final_rank: int | None
    is_starred: bool
    is_recruited: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SearchOut(BaseModel):
    id: uuid.UUID
    jd_text: str
    jd_filename: str | None
    search_strings: Any
    platform_scope: str
    created_at: datetime
    results: list[SearchResultOut]

    model_config = {"from_attributes": True}


class SearchSummary(BaseModel):
    id: uuid.UUID
    title: str                   # extracted display title
    jd_preview: str              # first 200 chars (shown on card hover)
    platform_scope: str
    created_at: datetime
    result_count: int
