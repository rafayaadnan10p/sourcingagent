"""
Web search provider module — Serper API (current provider).

Public interface:
    run_searches(queries: list[str]) -> list[dict]

Returns a flat list of result dicts:
    {
        "query":    str,   # the search string that produced this result
        "position": int,   # 1-based rank as returned by the search engine
        "url":      str,
        "title":    str,
        "snippet":  str,
    }

To swap providers later: implement the same return shape and update only this file.
"""

import sys
import httpx
from app.config import get_settings

# On Windows (local dev with corporate proxy): use truststore for SSL
# On Linux (Railway/production): use standard httpx SSL (certifi)
if sys.platform == 'win32':
    try:
        import ssl
        import truststore
        _ssl_verify = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except Exception:
        _ssl_verify = True  # fallback if truststore unavailable
else:
    _ssl_verify = True  # Linux: standard SSL works fine

_SERPER_ENDPOINT = "https://google.serper.dev/search"
_RESULTS_PER_QUERY = 20        # Serper charges per call, not per result — 20 is free
_SERPER_COST_PER_QUERY = 0.0   # Free plan: 2,500 queries/month included (update when upgrading)


def run_searches(queries: list[str]) -> list[dict]:
    """
    Run each query against the web search API and return all results as a
    flat list in the order they were retrieved.

    Args:
        queries: List of Boolean search strings (from Agent 1).

    Returns:
        Flat list of result dicts (see module docstring for shape).

    Raises:
        httpx.HTTPStatusError: On non-2xx responses from the search API.
        httpx.RequestError: On network-level failures.
    """
    settings = get_settings()
    headers = {
        "X-API-KEY": settings.serper_api_key,
        "Content-Type": "application/json",
    }

    successful_queries = 0
    all_results: list[dict] = []
    with httpx.Client(timeout=30, verify=_ssl_verify) as client:
        for query in queries:
            if not query or not query.strip():
                continue

            payload = {"q": query.strip(), "num": _RESULTS_PER_QUERY}
            try:
                response = client.post(_SERPER_ENDPOINT, json=payload, headers=headers)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                print(f"[websearch] Skipping query ({exc.response.status_code}): {query[:120]}")
                continue

            successful_queries += 1
            data = response.json()
            organic = data.get("organic", [])

            for item in organic:
                all_results.append({
                    "query":    query,
                    "position": item.get("position", 0),
                    "url":      item.get("link", ""),
                    "title":    item.get("title", ""),
                    "snippet":  item.get("snippet", ""),
                })

    serper_cost = successful_queries * _SERPER_COST_PER_QUERY
    plan_note = "free plan" if _SERPER_COST_PER_QUERY == 0 else f"est. ${serper_cost:.5f}"
    print(
        f"[serper]  Web search               "
        f"| queries={successful_queries} results={len(all_results)}"
        f" | {plan_note} (2,500 free/month)"
    )
    return all_results
