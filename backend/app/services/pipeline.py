"""
Pipeline service — orchestrates the full sourcing flow and persists results.

Public interface:
    run_pipeline(db, jd_text, platform_scope, jd_filename, user_id) -> Search
"""

import uuid
import re
from sqlalchemy.orm import Session

from app.agents.search_string_agent import generate_search_strings, detect_country, KNOWN_COUNTRY_SUBDOMAINS
from app.services.websearch import run_searches
from app.agents.relevance_agent import score_results
from app.models.user import User
from app.models.search import Search
from app.models.search_result import SearchResult

# Placeholder used until real auth is added
_PLACEHOLDER_EMAIL = "placeholder@internal"


def _get_or_create_placeholder_user(db: Session) -> uuid.UUID:
    user = db.query(User).filter(User.email == _PLACEHOLDER_EMAIL).first()
    if not user:
        user = User(email=_PLACEHOLDER_EMAIL, hashed_password="placeholder-no-login")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user.id


def run_pipeline(
    db: Session,
    jd_text: str,
    platform_scope: str,
    jd_filename: str | None = None,
    user_id: uuid.UUID | None = None,
    location_override: str = "not_specified",
    target_companies: str = "",
    open_to_work: bool = False,
) -> Search:
    """
    Full sourcing pipeline:
      1. Agent 1  — generate X-ray search strings from the JD
      2. Serper   — run each string against the search API
      3. Agent 2  — score and rank results for relevance
      4. Persist  — save search + results to the database

    Returns the newly created Search ORM object (with results loaded).
    """
    if user_id is None:
        user_id = _get_or_create_placeholder_user(db)

    # ── Agent 1 ───────────────────────────────────────────────────────────────
    search_strings = generate_search_strings(
        jd_text,
        platform_scope,
        location_override=location_override,
        target_companies=target_companies,
        open_to_work=open_to_work,
    )

    # ── Web search ────────────────────────────────────────────────────────────
    queries = [s["query"] for s in search_strings]
    raw_results = run_searches(queries)

    # Deduplicate by URL across queries (STRICT + BROAD can return the same profile)
    seen_urls: set[str] = set()
    unique_results = []
    for r in raw_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique_results.append(r)
    raw_results = unique_results

    if not raw_results:
        raise ValueError("No search results returned — all queries may have failed or returned nothing.")

    # ── Deterministic URL-based location penalty ──────────────────────────────
    # If the JD/override specifies a country, cap scores for clearly wrong-country URLs
    expected_country, _ = detect_country(location_override, jd_text)
    # Default to Pakistan for LinkedIn when no location explicitly specified
    if expected_country is None and platform_scope == "linkedin":
        expected_country = "pk"
    if expected_country:
        _country_re = re.compile(r'https?://([a-z]{2})\.linkedin\.com/', re.IGNORECASE)
        for r in raw_results:
            m = _country_re.match(r.get("url", ""))
            if m:
                url_country = m.group(1).lower()
                if url_country != expected_country and url_country in KNOWN_COUNTRY_SUBDOMAINS:
                    r["_location_mismatch"] = True

    # ── Agent 2 ───────────────────────────────────────────────────────────────
    ranked_results = score_results(jd_text, raw_results)

    # Apply hard cap on location-mismatched results
    if expected_country:
        for r in ranked_results:
            if r.get("_location_mismatch") and (r.get("relevance_score") or 0) > 0.5:
                r["relevance_score"] = 0.5
                r["relevance_reasoning"] = (r.get("relevance_reasoning") or "") + " [Score capped: URL subdomain indicates candidate is not in the required country.]"
        # Re-sort after capping and reassign final_rank
        ranked_results.sort(key=lambda r: r["relevance_score"], reverse=True)
        for i, r in enumerate(ranked_results):
            r["final_rank"] = i + 1 if i < 20 else None

    # ── Persist ───────────────────────────────────────────────────────────────
    search = Search(
        user_id=user_id,
        jd_text=jd_text,
        jd_filename=jd_filename,
        search_strings=search_strings,
        platform_scope=platform_scope,
    )
    db.add(search)
    db.flush()  # assigns search.id without committing yet

    for r in ranked_results:
        db.add(SearchResult(
            search_id=search.id,
            url=r["url"],
            title=r.get("title"),
            snippet=r.get("snippet"),
            original_position=r["position"],
            relevance_score=r.get("relevance_score"),
            relevance_reasoning=r.get("relevance_reasoning"),
            final_rank=r.get("final_rank"),
        ))

    db.commit()
    db.refresh(search)
    print(f"[pipeline] Search {search.id} complete — {len(ranked_results)} results saved.")
    return search
