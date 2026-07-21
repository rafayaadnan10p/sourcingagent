import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.limiter import limiter
from app.models.search import Search
from app.models.search_result import SearchResult
from app.schemas.jd import JDTextInput
from app.schemas.search import SearchOut, SearchSummary, SearchResultOut
from app.services.pipeline import run_pipeline
from app.utils.jd_parser import extract_search_title
from app.agents.jd_validator import validate_jd

router = APIRouter(tags=["Search"])
_settings = get_settings()
_RATE_LIMIT = f"{_settings.rate_limit_per_minute}/minute"


@router.post("/search", response_model=SearchOut)
@limiter.limit(_RATE_LIMIT)
def run_search(request: Request, payload: JDTextInput, db: Session = Depends(get_db)):
    """
    Full pipeline: JD text → search strings → web search → relevance scoring → DB save.
    Returns the complete ranked shortlist.
    """
    # Validate input is a real JD before spending API credits on the pipeline
    validation_error = validate_jd(payload.jd_text)
    if validation_error:
        raise HTTPException(status_code=422, detail=validation_error)
    search = run_pipeline(
        db=db,
        jd_text=payload.jd_text,
        platform_scope=payload.platform_scope,
        location_override=payload.location_override,
        target_companies=payload.target_companies,
        open_to_work=payload.open_to_work,
    )
    return search


@router.get("/searches", response_model=list[SearchSummary])
def list_searches(db: Session = Depends(get_db)):
    """List all past searches, newest first (for the Past Searches sidebar page)."""
    searches = db.query(Search).order_by(Search.created_at.desc()).all()
    return [
        SearchSummary(
            id=s.id,
            title=extract_search_title(s.jd_text),
            jd_preview=(s.jd_text[:200] + "…") if len(s.jd_text) > 200 else s.jd_text,
            platform_scope=s.platform_scope,
            created_at=s.created_at,
            result_count=len(s.results),
        )
        for s in searches
    ]


@router.get("/searches/{search_id}", response_model=SearchOut)
def get_search(search_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get the full results of a specific past search."""
    search = db.query(Search).filter(Search.id == search_id).first()
    if not search:
        raise HTTPException(status_code=404, detail="Search not found.")
    return search


@router.delete("/searches/{search_id}", status_code=204)
def delete_search(search_id: uuid.UUID, db: Session = Depends(get_db)):
    """Permanently delete a search and all its results."""
    search = db.query(Search).filter(Search.id == search_id).first()
    if not search:
        raise HTTPException(status_code=404, detail="Search not found.")
    db.delete(search)
    db.commit()


@router.patch("/results/{result_id}/star", response_model=SearchResultOut)
def toggle_star(result_id: uuid.UUID, db: Session = Depends(get_db)):
    """Star or unstar a candidate profile (toggles the current state)."""
    result = db.query(SearchResult).filter(SearchResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found.")
    result.is_starred = not result.is_starred
    db.commit()
    db.refresh(result)
    return result


@router.patch("/results/{result_id}/recruit", response_model=SearchResultOut)
def toggle_recruit(result_id: uuid.UUID, db: Session = Depends(get_db)):
    """Mark or unmark a candidate as recruited (toggles the current state)."""
    result = db.query(SearchResult).filter(SearchResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found.")
    result.is_recruited = not result.is_recruited
    db.commit()
    db.refresh(result)
    return result


@router.get("/results/starred", response_model=list[SearchResultOut])
def get_starred_profiles(db: Session = Depends(get_db)):
    """All starred profiles across all searches (Starred Profiles sidebar page)."""
    return (
        db.query(SearchResult)
        .filter(SearchResult.is_starred.is_(True))
        .order_by(SearchResult.created_at.desc())
        .all()
    )
