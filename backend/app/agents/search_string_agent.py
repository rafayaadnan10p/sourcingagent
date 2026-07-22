"""
Agent 1 — Search String Generation

Public interface:
    generate_search_strings(jd_text: str, platform_scope: str) -> list[dict]

Returns a list of dicts:
    [{"label": "LinkedIn X-Ray (strict)", "query": "site:linkedin.com/in ..."}]
"""

import json
import re
from openai import OpenAI
from app.config import get_settings
from app.utils.token_logger import log_tokens

# site: operators per platform
_PLATFORM_SITE: dict[str, str] = {
    "linkedin": "site:linkedin.com/in",
    "github": "site:github.com",
    "upwork": "site:upwork.com/freelancers",
    "fiverr": "site:fiverr.com/s",
    "behance": "site:behance.net",
}

# Country-specific LinkedIn subdomains for accurate geo-filtering
# Key: lowercase keyword found in location/JD → Value: (subdomain, site: operator)
_LOCATION_SUBDOMAIN: dict[str, tuple[str, str]] = {
    "islamabad":        ("pk", "site:pk.linkedin.com/in"),
    "karachi":          ("pk", "site:pk.linkedin.com/in"),
    "lahore":           ("pk", "site:pk.linkedin.com/in"),
    "pakistan":         ("pk", "site:pk.linkedin.com/in"),
    "dubai":            ("ae", "site:ae.linkedin.com/in"),
    "abu dhabi":        ("ae", "site:ae.linkedin.com/in"),
    "uae":              ("ae", "site:ae.linkedin.com/in"),
    "india":            ("in", "site:in.linkedin.com/in"),
    "bangalore":        ("in", "site:in.linkedin.com/in"),
    "mumbai":           ("in", "site:in.linkedin.com/in"),
    "london":           ("gb", "site:uk.linkedin.com/in"),
    "united kingdom":   ("gb", "site:uk.linkedin.com/in"),
    "germany":          ("de", "site:de.linkedin.com/in"),
}

# All known non-global subdomains — used for penalising wrong-country results
KNOWN_COUNTRY_SUBDOMAINS: set[str] = {"pk", "ae", "de", "in", "ca", "gb", "uk", "fr", "au", "sg", "nl", "se"}


def detect_country(location_override: str, jd_text: str) -> tuple[str | None, str | None]:
    """
    Returns (country_code, site_operator) if a known location is detected, else (None, None).
    Checks location_override first, then first 600 chars of JD.
    """
    search_text = (location_override + " " + jd_text[:600]).lower()
    for keyword, (code, site_op) in _LOCATION_SUBDOMAIN.items():
        if keyword in search_text:
            return code, site_op
    return None, None

_SYSTEM_PROMPT = """
You are a technical sourcer's Boolean search assistant.

You receive either a job description (JD) OR a person's name/name+skills. Handle each differently:

━━ CASE 1 — Job description input ━━
Extract from the JD:
- Core job title + realistic synonyms recruiters actually use
- Must-have skills / tools (explicitly required)
- Nice-to-have skills (mentioned but not hard requirements)
- Seniority / years of experience
- Location (city, country)

Generate exactly three queries:
  1. STRICT — job title + must-have skills (2–3 max). If location is in JD, include it.
     Do NOT chain more than 4 AND conditions total.
  2. BROAD — job title synonyms OR'd together + skills grouped with OR. If location is
     in JD, include it. Do NOT use more than 4 AND conditions total.
  3. EXTENDED (country-wide) — same as BROAD but drop the specific city, keeping only the
     country (e.g. "Pakistan" not "Islamabad, Pakistan"). Do NOT use more than 3 AND conditions.

Location rule (CRITICAL for JD searches):
  - Use quoted "City, Country" phrase in queries 1 and 2 (e.g. "Islamabad, Pakistan").
  - For query 1, also add intitle:"City" to strongly filter for currently-based candidates.
    Example: intitle:"Islamabad" site:pk.linkedin.com/in "Sr QA Engineer" AND Python
  - If the JD has NO location, all three queries are location-free.

━━ CASE 2 — Person name input ━━
If the input is a person's name (optionally with a role/skill hint), e.g.:
  "Ahmad Hanif" or "Ahmad Hanif, python" or "Sarah Khan - AI developer"

Generate exactly three simple name-focused queries. Do NOT use complex Boolean logic:
  1. NAME STRICT — "FirstName LastName" <site_op> [top skill if provided]
     Example: "Ahmad Hanif" site:pk.linkedin.com/in python
  2. NAME BROAD  — "FirstName LastName" <site_op>
     Example: "Ahmad Hanif" site:pk.linkedin.com/in
  3. NAME EXTENDED — "FirstName LastName" (no site: restriction, catches other platforms)
     Example: "Ahmad Hanif" linkedin

━━ Shared output rules ━━
- Return ONLY valid JSON — no markdown fences, no prose, no extra keys.
- The JSON must match this exact shape:
  {
    "search_strings": [
      {"label": "<short descriptive name>", "query": "<full ready-to-paste Google search string>"}
    ]
  }
- Apply the site: operator exactly as instructed. Do not add or change it.
- Google returns very few results with too many AND conditions — keep queries short.
- Do not put any explanation inside the query field — only the search string itself.
""".strip()


def _build_user_message(jd_text: str, platform_scope: str, location_override: str, target_companies: str, open_to_work: bool) -> str:
    if platform_scope == "all":
        site_instruction = (
            "Generate queries for ALL of these platforms, clearly labelled:\n"
            "- LinkedIn profiles  → site:linkedin.com/in\n"
            "- GitHub profiles    → site:github.com\n"
            "- Upwork profiles    → site:upwork.com/freelancers\n"
            "- Behance portfolios → site:behance.net\n"
            "- Fiverr gigs        → site:fiverr.com\n"
            "Plus one broad query with NO site: restriction for general web search."
        )
    else:
        if platform_scope == "linkedin":
            country_code, country_site = detect_country(location_override, jd_text)
            # Default to Pakistan (pk.linkedin.com) when no location is detected
            if country_code is None:
                country_code = "pk"
            effective_site = country_site or "site:pk.linkedin.com/in"
            country_names = {
                "pk": "Pakistan", "ae": "UAE", "in": "India",
                "de": "Germany", "gb": "United Kingdom", "ca": "Canada",
            }
            country_name = country_names.get(country_code, "")
        else:
            effective_site = _PLATFORM_SITE.get(platform_scope, "")
            country_name = ""

        site_instruction = (
            f"Queries 1 and 2 must use this site: operator exactly: {effective_site}\n"
            "Query 3 (EXTENDED / NAME EXTENDED) must use site:linkedin.com/in (global, no country prefix) "
            "to catch candidates who may not appear in the country-specific subdomain.\n"
            + (f"For the EXTENDED query, use '{country_name}' as the location (not the specific city)." if country_name else
               "For the EXTENDED query, omit location entirely.")
        )

    extras = []

    if location_override and location_override != "not_specified":
        extras.append(
            f"Location override: The user has explicitly selected '{location_override}' as the target location. "
            f"Include '{location_override}' in ALL queries (queries 1 and 2), even if the JD does not mention a location. "
            f"This takes priority over any location mentioned in the JD."
        )

    if target_companies:
        companies = [c.strip() for c in target_companies.split(",") if c.strip()]
        if companies:
            company_list = " OR ".join(f'"{c}"' for c in companies)
            extras.append(
                f"Target companies: The user wants to source candidates from specific companies. "
                f"Include ({company_list}) in the BROAD and EXTENDED queries."
            )

    if open_to_work and platform_scope == "linkedin":
        extras.append(
            'Open to Work filter: Add ("#OpenToWork" OR "Open to work") to ALL queries '
            "to surface candidates actively seeking jobs."
        )

    extra_block = ("\n\nAdditional sourcing filters:\n" + "\n".join(f"- {e}" for e in extras)) if extras else ""

    return (
        f"Platform scope: {platform_scope}\n"
        f"{site_instruction}"
        f"{extra_block}\n\n"
        f"Job Description:\n{jd_text}"
    )


def generate_search_strings(
    jd_text: str,
    platform_scope: str = "all",
    location_override: str = "not_specified",
    target_companies: str = "",
    open_to_work: bool = False,
) -> list[dict]:
    """Generate X-ray Boolean search strings from a job description."""
    if platform_scope not in {"all", "linkedin", "github", "upwork", "fiverr", "behance"}:
        raise ValueError(f"Invalid platform_scope: {platform_scope!r}")

    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)

    response = client.chat.completions.create(
        model=settings.openai_model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_message(jd_text, platform_scope, location_override, target_companies, open_to_work)},
        ],
        temperature=0.2,
    )

    raw = response.choices[0].message.content or ""
    log_tokens("Agent 1 (search strings)", settings.openai_model, response.usage)

    try:
        parsed = json.loads(raw)
        results: list[dict] = parsed["search_strings"]
    except (json.JSONDecodeError, KeyError) as exc:
        raise ValueError(f"Agent 1 returned unexpected JSON structure: {exc}\n\nRaw:\n{raw}") from exc

    return results
