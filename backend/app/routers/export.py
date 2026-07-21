import uuid
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.search import Search
from app.models.search_result import SearchResult
from app.export.excel import generate_excel
from app.export.csv_export import generate_csv
from app.utils.jd_parser import extract_search_title

router = APIRouter(tags=["Export"])


def _safe_filename(text: str, max_len: int = 40) -> str:
    """Convert text to a safe filename segment (no special chars, underscores for spaces)."""
    text = re.sub(r'[^\w\s\-]', '', text)   # keep word chars, spaces, hyphens
    text = re.sub(r'[\s\-]+', '_', text.strip())
    return text[:max_len]


def _build_filename(search: Search, extension: str) -> str:
    raw_title = extract_search_title(search.jd_text)
    # raw_title is like "Sr QA Engineer | Islamabad | 5–8 yrs"
    parts = [p.strip() for p in raw_title.split('|')]
    title_part = _safe_filename(parts[0]) if len(parts) > 0 else "Search"
    # Multiple locations → abbreviate each to first 3 chars uppercase, join with _
    # e.g. "Islamabad or Karachi or Lahore" → "ISL_KAR_LAH"
    raw_location = parts[1] if len(parts) > 1 else ""
    if raw_location:
        loc_parts = re.split(r'\s*(?:or|and|/|,)\s*', raw_location.strip(), flags=re.IGNORECASE)
        location_part = '_'.join(p.strip()[:3].upper() for p in loc_parts if p.strip())
    else:
        location_part = "No_Location"
    date_part = search.created_at.strftime('%Y-%m-%d')

    segments = [s for s in [title_part, location_part, date_part] if s]
    return '_'.join(segments) + extension


def _get_all_results(search_id: uuid.UUID, db: Session) -> tuple:
    """Returns (search, results) for the given search_id."""
    search = db.query(Search).filter(Search.id == search_id).first()
    if not search:
        raise HTTPException(status_code=404, detail="Search not found.")
    results = db.query(SearchResult).filter(SearchResult.search_id == search_id).all()
    if not results:
        raise HTTPException(status_code=404, detail="No results found for this search.")
    return search, results


@router.get("/searches/{search_id}/export/excel")
def export_excel(search_id: uuid.UUID, db: Session = Depends(get_db)):
    """Download all results as an Excel (.xlsx) file — shortlist first, then others."""
    search, results = _get_all_results(search_id, db)
    xlsx_bytes = generate_excel(results)
    filename = _build_filename(search, '.xlsx')
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
    )


@router.get("/searches/{search_id}/export/csv")
def export_csv(search_id: uuid.UUID, db: Session = Depends(get_db)):
    """Download all results as a CSV file — shortlist first, then others."""
    search, results = _get_all_results(search_id, db)
    csv_content = generate_csv(results)
    filename = _build_filename(search, '.csv')
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
    )
