"""
Deterministic JD title extractor.

extract_search_title(jd_text) -> str

Returns a display title in the format:
    "Job Title | Location | 5–8 yrs"

Handles two common JD formats:
  - Inline:    **Job Title:** Senior Engineer  (markdown / pasted text)
  - Next-line: Job Title\n Senior Engineer     (PDF-extracted)

No LLM involved — same input always produces the same output.
"""

import re


def extract_search_title(jd_text: str) -> str:
    # Strip markdown bold markers and normalise whitespace
    text = re.sub(r"\*{1,3}", "", jd_text.strip())
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    title = _extract_field(text, lines, ["job title", "title", "role", "position"])
    location = _extract_field(text, lines, ["location", "city"])
    experience = _extract_experience(text, lines)

    parts = [p for p in [title, location, experience] if p]
    if len(parts) >= 2:
        return " | ".join(parts)
    if title:
        return title[:80]
    # Last resort: first non-empty line of the JD
    return lines[0][:60] if lines else jd_text[:60]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_field(text: str, lines: list[str], labels: list[str]) -> str | None:
    label_re = "|".join(re.escape(l) for l in labels)

    # Any word that looks like a field label (stops value from running into the next field)
    _stop = r"(?=\s*(?:job\s+type|job\s+title|job\s+level|title|role|position|location|city|experience|level|type|start|date|company|department)\s*[:\-]|\s*\n|$)"

    # Pattern 1 — inline "Label: value" (same line, after stripping **)
    m = re.search(
        rf"(?:{label_re})\s*[:\-]\s*(.+?){_stop}",
        text,
        re.IGNORECASE,
    )
    if m:
        val = _clean_value(m.group(1))
        if val:
            return val

    # Pattern 2 — next-line "Label\nValue" (PDF-extracted)
    for i, line in enumerate(lines):
        if line.lower() in labels and i + 1 < len(lines):
            val = _clean_value(lines[i + 1])
            if val:
                return val

    return None


def _extract_experience(text: str, lines: list[str]) -> str | None:
    # Inline label: "Experience: 5–8 years"
    m = re.search(
        r"experience\s*[:\-]\s*(.+?)(?:\s*\n|$)",
        text,
        re.IGNORECASE,
    )
    if m:
        val = m.group(1).strip()
        # Try to pull just the years part from the value
        yr = re.search(r"(\d+\s*[–\-]\s*\d+|\d+\+)\s*years?", val, re.IGNORECASE)
        if yr:
            return _format_experience(yr.group(1))
        if len(val) < 30:
            return val

    # Next-line "Experience\n5–8 years"
    for i, line in enumerate(lines):
        if line.lower() == "experience" and i + 1 < len(lines):
            val = lines[i + 1].strip()
            yr = re.search(r"(\d+\s*[–\-]\s*\d+|\d+\+)\s*years?", val, re.IGNORECASE)
            if yr:
                return _format_experience(yr.group(1))
            if len(val) < 30:
                return val

    # Bare pattern anywhere in text: "5–8 years"
    m = re.search(r"(\d+\s*[–\-]\s*\d+)\s*years?", text, re.IGNORECASE)
    if m:
        return _format_experience(m.group(1))
    m = re.search(r"(\d+)\+\s*years?", text, re.IGNORECASE)
    if m:
        return f"{m.group(1)}+ yrs"

    return None


def _clean_value(val: str) -> str | None:
    """Strip trailing junk and return None if the value looks like a label itself."""
    val = val.strip().rstrip("*:").strip()
    # Cut at pipe or opening parenthesis that introduces meta-info
    val = re.split(r"\s*[\|(]", val)[0].strip()
    if not val or len(val) > 80:
        return None
    # Reject if it looks like a label (single word, all-caps, or known label word)
    if re.fullmatch(r"[A-Z\s]+", val) and len(val.split()) <= 2:
        return None
    return val


def _format_experience(raw: str) -> str:
    # Normalise en-dash and spaces: "5 - 8" → "5–8 yrs"
    normalised = re.sub(r"\s*[-–]\s*", "–", raw.strip())
    return f"{normalised} yrs"
