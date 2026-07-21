/**
 * Deterministic JD title extractor — TypeScript port of app/utils/jd_parser.py
 *
 * Returns "Job Title | Location | X–Y yrs" from raw JD text.
 * Handles both inline (**Label:** value) and next-line (Label\nValue) formats.
 */

export function extractSearchTitle(jdText: string): string {
  // Strip markdown bold markers
  const text = jdText.replace(/\*{1,3}/g, '').trim()
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean)

  const title = extractField(text, lines, ['job title', 'title', 'role', 'position'])
  const location = extractField(text, lines, ['location', 'city'])
  const experience = extractExperience(text, lines)

  const parts = [title, location, experience].filter(Boolean)
  if (parts.length >= 2) return parts.join(' | ')
  if (title) return title.slice(0, 80)
  return lines[0]?.slice(0, 60) ?? jdText.slice(0, 60)
}

const STOP =
  /(?=\s*(?:job\s+type|job\s+title|job\s+level|title|role|position|location|city|experience|level|type|start|date|company|department)\s*[:\-]|\s*\n|$)/i

function extractField(text: string, lines: string[], labels: string[]): string | null {
  const labelRe = labels.map(l => l.replace(/\s+/, '\\s+')).join('|')

  // Pattern 1 — inline "Label: value"
  const inlineRe = new RegExp(`(?:${labelRe})\\s*[:\\-]\\s*(.+?)` + STOP.source, 'i')
  const inlineMatch = text.match(inlineRe)
  if (inlineMatch) {
    const val = cleanValue(inlineMatch[1])
    if (val) return val
  }

  // Pattern 2 — next-line "Label\nValue"
  for (let i = 0; i < lines.length - 1; i++) {
    if (labels.includes(lines[i].toLowerCase())) {
      const val = cleanValue(lines[i + 1])
      if (val) return val
    }
  }

  return null
}

function extractExperience(text: string, lines: string[]): string | null {
  // Inline "Experience: 5–8 years"
  const inlineMatch = text.match(/experience\s*[:\-]\s*(.+?)(?:\s*\n|$)/i)
  if (inlineMatch) {
    const yr = inlineMatch[1].match(/(\d+\s*[–\-]\s*\d+|\d+\+)\s*years?/i)
    if (yr) return formatExp(yr[1])
    if (inlineMatch[1].trim().length < 30) return inlineMatch[1].trim()
  }

  // Next-line "Experience\n5–8 years"
  for (let i = 0; i < lines.length - 1; i++) {
    if (lines[i].toLowerCase() === 'experience') {
      const yr = lines[i + 1].match(/(\d+\s*[–\-]\s*\d+|\d+\+)\s*years?/i)
      if (yr) return formatExp(yr[1])
      if (lines[i + 1].length < 30) return lines[i + 1]
    }
  }

  // Bare "5–8 years" anywhere
  const bare = text.match(/(\d+\s*[–\-]\s*\d+)\s*years?/i)
  if (bare) return formatExp(bare[1])
  const plus = text.match(/(\d+)\+\s*years?/i)
  if (plus) return `${plus[1]}+ yrs`

  return null
}

function cleanValue(val: string): string | null {
  let v = val.trim().replace(/[*:|]+$/, '').trim()
  v = v.split(/\s*[|(]/, 1)[0].trim()
  if (!v || v.length > 80) return null
  if (/^[A-Z\s]+$/.test(v) && v.split(' ').length <= 2) return null
  return v
}

function formatExp(raw: string): string {
  return raw.trim().replace(/\s*[-–]\s*/, '–') + ' yrs'
}

