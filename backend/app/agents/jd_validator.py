"""
JD Validator — uses gpt-4o-mini to check if the input is a real job description.

Public interface:
    validate_jd(text: str) -> str | None
    Returns None if valid, or an error message string if not a JD.
"""

from openai import OpenAI
from app.config import get_settings
from app.utils.token_logger import log_tokens

_VALIDATION_MODEL = "gpt-4o-mini"

_SYSTEM_PROMPT = """You are a gatekeeper for a candidate sourcing tool.
Your only job is to decide if the user's input is a job description (JD).

A job description typically describes:
- A role or position being hired for
- Required or preferred skills / qualifications
- Responsibilities or duties
- Location, experience level, or other hiring requirements

Reply with ONLY one of these two responses:
- YES   (if the input is a job description or plausibly describes a role being hired for)
- NO    (if the input is clearly not a job description)

Be lenient: a short JD, an informal job posting, or a partially formatted JD should still be YES.
Only reply NO for input that is completely unrelated to hiring (e.g. chat messages, articles, code, random text).
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
            "This is a sourcing tool designed for job descriptions. "
            "The input you provided doesn't appear to be a JD. "
            "Please provide a job description with role details, skills, and requirements."
        )

    return None  # valid JD
