"""
Agent 2 — Relevance Scoring

Public interface:
    score_results(jd_text: str, results: list[dict]) -> list[dict]

Takes the flat results list from websearch.run_searches() and returns the same
list enriched with two new keys on every item:
    "relevance_score":     float  — 0.0 to 10.0
    "relevance_reasoning": str    — one sentence explaining the score

The entire batch is scored in a single LLM call to keep API costs low.
The top 10 by score are then assigned a final_rank (1–10).
"""

import json
from openai import OpenAI
from app.config import get_settings
from app.utils.token_logger import log_tokens

_SYSTEM_PROMPT = """
You are a technical recruiter's assistant evaluating candidate search results
against a job description.

You will receive:
1. A job description (JD).
2. A numbered list of search results, each with a URL, title, and snippet.

Your task:
- For each result, score how relevant the candidate profile appears to be for
  the role described in the JD, based ONLY on what is visible (URL, title, snippet).
- Score from 0.0 (completely irrelevant) to 10.0 (perfect match).
- Write 2–3 sentences of reasoning per result that:
    1. State what matches (title, skills, seniority, location)
    2. State what is missing or unclear (skills not mentioned, wrong location, insufficient experience)
    3. Justify the score based on both the strengths and the gaps

Location rule (CRITICAL):
- If the JD specifies a location, candidates from a different location must score
  1.0 or lower — location is a hard disqualifier, not a preference.
- Use the URL subdomain to determine location: pk.linkedin.com = Pakistan,
  ae.linkedin.com = UAE, de.linkedin.com = Germany, in.linkedin.com = India,
  ca.linkedin.com = Canada, gb/uk.linkedin.com = UK.
  If the JD requires Pakistan and the URL shows ae. or de. or in. etc., score 0.5 or lower.
- www.linkedin.com URLs are location-neutral — infer location from the snippet.
- IMPORTANT — current vs past location: if the snippet mentions the required city
  only in a past experience context (e.g. "worked in Islamabad 2018–2020" or
  "previous company in Islamabad") but the candidate’s current location is elsewhere,
  treat them as the wrong location and score ≤1.0. Only count the city as matching
  if it appears as CURRENT location (near the start of the snippet or in the headline).
- Only ignore the location rule if the JD explicitly says "remote" or "flexible location".

Return ONLY valid JSON — no markdown fences, no extra keys — matching this exact shape:
{
  "scores": [
    {"index": <int>, "relevance_score": <float>, "relevance_reasoning": "<string>"}
  ]
}

The "index" field must match the index number given in the input list (0-based).
Score every result; do not skip any.
""".strip()


def _build_user_message(jd_text: str, results: list[dict]) -> str:
    lines = ["Job Description:\n", jd_text, "\n\nSearch Results:\n"]
    for i, r in enumerate(results):
        lines.append(
            f"[{i}] URL: {r['url']}\n"
            f"    Title: {r.get('title', '')}\n"
            f"    Snippet: {r.get('snippet', '')}\n"
        )
    return "\n".join(lines)


def score_results(jd_text: str, results: list[dict]) -> list[dict]:
    """
    Score each search result for relevance to the JD.

    Args:
        jd_text:  Full job description text.
        results:  List of result dicts from websearch.run_searches().

    Returns:
        Same list with "relevance_score" and "relevance_reasoning" added to
        each item. Items are sorted by score descending. The top 10 also
        receive a "final_rank" key (1–10); the rest get final_rank=None.

    Raises:
        ValueError: If the LLM returns malformed JSON.
        openai.OpenAIError: On API failures.
    """
    if not results:
        return results

    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)

    response = client.chat.completions.create(
        model=settings.openai_model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_message(jd_text, results)},
        ],
        temperature=0.1,
    )

    raw = response.choices[0].message.content or ""
    log_tokens("Agent 2 (relevance)", settings.openai_model, response.usage)

    try:
        parsed = json.loads(raw)
        scores: list[dict] = parsed["scores"]
    except (json.JSONDecodeError, KeyError) as exc:
        raise ValueError(
            f"Agent 2 returned unexpected JSON structure: {exc}\n\nRaw:\n{raw}"
        ) from exc

    # Apply scores back onto the results list
    score_map = {item["index"]: item for item in scores}
    for i, result in enumerate(results):
        score_item = score_map.get(i, {})
        result["relevance_score"] = score_item.get("relevance_score", 0.0)
        result["relevance_reasoning"] = score_item.get("relevance_reasoning", "")

    # Sort by score descending, then assign final_rank to top 20
    results.sort(key=lambda r: r["relevance_score"], reverse=True)
    for i, result in enumerate(results):
        result["final_rank"] = i + 1 if i < 20 else None

    return results
