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

When given a job description (JD), generate X-ray Google search strings that a recruiter
can paste directly into Google to find candidate profiles on the web.

What to extract from the JD:
- Core job title + realistic synonyms recruiters actually use
- Must-have skills / tools (explicitly required)
- Nice-to-have skills (mentioned but not hard requirements)
- Seniority / years of experience
- Location (city, country)

Output rules:
- Return ONLY valid JSON — no markdown fences, no prose, no extra keys.
- The JSON must match this exact shape:
  {
    "search_strings": [
      {"label": "<short descriptive name>", "query": "<full ready-to-paste Google search string>"}
    ]
  }
- Each query must be a valid Google search string using Boolean operators:
  AND, OR, NOT, quotes for exact phrases, parentheses for grouping.
- Always generate exactly these three queries:
    1. STRICT — job title + must-have skills (2–3 max). If location is in JD, include it.
       Do NOT chain more than 4 AND conditions total.
    2. BROAD — job title synonyms OR'd together + skills grouped with OR. If location is
       in JD, include it. Do NOT use more than 4 AND conditions total.
    3. EXTENDED — same as BROAD but drop the specific city, keeping only the country
       if one was detected (e.g. use "Pakistan" not "Islamabad, Pakistan"). If no
       country was detected, omit location entirely. This surfaces strong candidates
       who may be in other cities within the same country or willing to relocate.
       Label it "EXTENDED (country-wide)". Do NOT use more than 3 AND conditions.
- Location rule (CRITICAL):
    - If the JD specifies a location, use it as a quoted "City, Country" phrase
      (e.g. "Islamabad, Pakistan") in queries 1 and 2. LinkedIn shows CURRENT location
      in this exact format — this avoids matching candidates who only mention the city
      in past experience. Do NOT use just the city name alone.
    - For the STRICT query (query 1), also add intitle:"City" — LinkedIn page titles
      include current location so this strongly filters for currently-based candidates.
      Example: intitle:"Islamabad" site:pk.linkedin.com/in "Sr QA Engineer" AND Python
    - Query 3 (EXTENDED) intentionally omits location as a fallback only.
    - If the JD does NOT specify a location, all three queries are location-free.
- Google returns very few results when there are too many AND conditions.
  Fewer ANDs = more results. This is critical.
- Apply the site: operator exactly as instructed. Do not add or change it.
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
            effective_site = country_site or _PLATFORM_SITE["linkedin"]
            country_names = {
                "pk": "Pakistan", "ae": "UAE", "in": "India",
                "de": "Germany", "gb": "United Kingdom", "ca": "Canada",
            }
            country_name = country_names.get(country_code or "", "")
        else:
            effective_site = _PLATFORM_SITE.get(platform_scope, "")
            country_name = ""

        site_instruction = (
            f"Generate queries restricted to: {effective_site}\n"
            "All queries (including EXTENDED) must include this site: operator exactly as shown.\n"
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
