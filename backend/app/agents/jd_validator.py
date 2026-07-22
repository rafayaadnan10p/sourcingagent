"""
JD Validator — uses gpt-4o-mini to check if the input is a real job description.

Public interface:
    validate_jd(text: str) -> str | None
    Returns None if valid, or an error message string if not a JD.
"""

import os
import json
from openai import OpenAI
from app.config import get_settings
from app.utils.token_logger import log_tokens

# Clear any proxy env vars that might block outbound connections on cloud platforms
for _var in ('HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy'):
    os.environ.pop(_var, None)

_VALIDATION_MODEL = "gpt-4o-mini"

_SYSTEM_PROMPT = """You are a gatekeeper for a candidate sourcing tool.
Your job is to decide if the user's input is useful for finding candidates.

Say YES for ANY of the following:
- A job description (full or partial, formal or informal)
- A person's name (e.g. "John Smith", "Ahmed Khan")
- A name plus context (e.g. "Sarah Lee - Python developer at Google")
- A role title or skill set
- Any text that could reasonably help source or identify candidates

Reply with ONLY one of these two responses:
- YES   (if the input could plausibly be used to find or identify a candidate)
- NO    (if the input is completely unrelated to people or hiring — e.g. a news article, a recipe, random code, or gibberish)

When in doubt, say YES.
"""


def validate_jd(text: str) -> str | None:
    """
    Returns None if the text is a valid JD.
    Returns an error message string if it is not.
    """
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)

    # Only send the first 800 chars — enough to judge, cheap to process
    snippet = text.strip()[:800]

    response = client.chat.completions.create(
        model=_VALIDATION_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user",   "content": snippet},
        ],
        max_tokens=5,
        temperature=0,
    )

    log_tokens("JD Validator", _VALIDATION_MODEL, response.usage)

    answer = (response.choices[0].message.content or "").strip().upper()

    if answer.startswith("NO"):
        return (
            "The input doesn't look like something that can be used to find candidates. "
            "Try entering a job description, a person's name, a role title, or a list of skills."
        )

    return None  # valid JD
