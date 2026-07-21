/**
 * Client-side JD validation.
 * Returns an error message string if the input is not a job description,
 * or null if it passes and should be processed.
 *
 * Deliberately lenient — designed to catch obviously irrelevant input
 * (greetings, random text, URLs) without ever rejecting a real JD.
 */

const MIN_WORDS = 35

// A broad list — virtually every real JD contains at least 2 of these
const JD_KEYWORDS = [
  'experience', 'years', 'skills', 'requirements', 'responsibilities',
  'role', 'position', 'job', 'title', 'qualifications', 'candidate',
  'engineer', 'developer', 'manager', 'analyst', 'designer', 'architect',
  'consultant', 'specialist', 'lead', 'senior', 'junior', 'intern',
  'hire', 'hiring', 'apply', 'team', 'company', 'organization',
  'proficient', 'knowledge', 'ability', 'preferred', 'required', 'minimum',
  'degree', 'bachelor', 'master', 'certification', 'salary', 'benefits',
  'onsite', 'remote', 'hybrid', 'full-time', 'part-time', 'contract',
  'location', 'islamabad', 'karachi', 'lahore', 'pakistan',
]

const MIN_KEYWORD_MATCHES = 2

export function validateJD(text: string): string | null {
  const cleaned = text.trim()

  if (!cleaned) return 'Please provide a job description.'

  const words = cleaned.split(/\s+/).filter(Boolean)
  if (words.length < MIN_WORDS) {
    return `This is a sourcing tool for job descriptions. The input seems too short to be a JD (${words.length} words). Please paste the full job description.`
  }

  const lower = cleaned.toLowerCase()
  const matchCount = JD_KEYWORDS.filter((kw) => lower.includes(kw)).length

  if (matchCount < MIN_KEYWORD_MATCHES) {
    return `This is a tool for pulling candidate profiles from job descriptions. The input doesn't look like a JD — please provide a job description with role details, skills, and requirements.`
  }

  return null // passes
}

