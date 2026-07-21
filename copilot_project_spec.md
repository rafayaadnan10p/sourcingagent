# AI Sourcing Agent — Full Project Spec for Copilot

Read this in full before generating code. It covers what we're building, what's already
done, what's blocked right now, and requirements for security, the database, and export
features. Ask before making architectural decisions not covered here.

## How to work on this

Act as an expert software engineer, not a code-completion tool. Concretely:

- Write clean, well-structured code. No redundant or duplicated logic, if the same thing
  is needed twice, factor it into a shared function.
- Before writing or changing any significant piece of code (a new endpoint, a new
  component, a schema change, adding a dependency), tell me in simple, plain language what
  you're about to do and why, and wait for me to confirm before doing it. Don't just go
  ahead and generate large chunks of code silently.
- If something in this spec is ambiguous or you see a better way to do it, ask me rather
  than guessing and moving forward.
- Small, incremental changes I can review and test are better than large ones I can't
  easily check.

## Tech stack

These are fixed choices, not open questions:

- **Backend:** FastAPI (Python)
- **Frontend:** React
- **Database:** PostgreSQL
- **LLM:** OpenAI API (see Current status for model/key details)
- **Web search:** Serper (for now, see Current status)

## Context

I'm an intern at a software company, building this as a long-term internal product for the
company, not a throwaway prototype. It will be used by the HR team on an ongoing basis after
I hand it off, and it will handle real candidate data, so it needs to be built securely from
day one, not patched for security later. Treat every recommendation in this spec, especially
the security section, as a hard requirement, not a nice-to-have.

## What this project is

An internal HR tool that automates X-ray sourcing. Today, HR sourcers manually paste a job
description into Claude or ChatGPT using a prompt they've written (shown below), get back
Boolean/X-ray search strings, and then manually copy-paste those strings into Google one at
a time to retrieve candidate URLs. They then judge each result's relevance themselves by
reading what's visible in the search result (title, snippet, URL). This tool automates that
entire flow: JD in, ranked candidate shortlist out, including a relevance check based on
what's visible in the web search results (title/snippet/URL), which ranks profiles from most
to least relevant.

This is the exact prompt HR currently pastes into Claude/ChatGPT by hand to generate the
search strings. Use it as the reference for what the automated search-string generation
agent should reproduce:

```
Boolean Sourcing Assistant
You are a technical sourcer's Boolean assistant. When the user pastes a job description
(JD), output ready-to-paste search strings. Do not ask follow-up questions unless the JD
is missing a job title or a location.

What to extract from the JD
- Core job title + realistic synonyms recruiters actually use
- Must-have skills / tools
- Seniority and years of experience
- Location

Output exactly these four blocks
1) GOOGLE X-RAY (LinkedIn profiles) — strict version
[... additional output blocks follow this in the original prompt ...]
```

The automated agent should replicate this extraction logic and output format, since it's
already proven to work for the HR team, just remove the manual copy-paste steps around it.

## End-to-end flow

1. **Input** — JD uploaded as a PDF or pasted as text.
2. **Search String Generation (Agent 1)** — an LLM reads the JD and generates X-ray Boolean
   search strings.
3. **Search Execution** — those strings are run against a web search API (Serper for now),
   returning candidate profile URLs + snippets in their original order.
4. **Results Table** — all results shown in original search-engine order.
5. **Relevance Scoring (Agent 2)** — an LLM scores each result's snippet against the JD.
6. **Shortlist** — top 10 most relevant profiles are surfaced, re-ranked, each with a
   reasoning string explaining why it was ranked where it was.
7. **Export** — from the shortlist page, the user can download or export the results (see
   Export Features below).
8. **Persistence** — every search (JD, generated strings, results, final ranking) is saved
   to the database so past searches can be revisited later.

## Current status

Nothing has been set up yet. This is a brand new, empty repository. Start from scratch:
repo structure, backend, frontend, all of it. The Streamlit prototype mentioned earlier in
this project's history was a separate, standalone proof of concept, not part of this repo,
and should not be assumed to exist here. Do not assume any files, folders, or dependencies
already exist, confirm the empty state and build up from there.

- **We have the OpenAI API key** — use the OpenAI API directly for both agents (search
  string generation and relevance scoring). Use the standard `openai` Python client:

  ```python
  from openai import OpenAI
  import os

  client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

  response = client.chat.completions.create(
      model=os.getenv("OPENAI_MODEL"),  # keep this configurable, see model choice below
      messages=[...],
  )
  ```

  Keep `OPENAI_API_KEY` and `OPENAI_MODEL` in `.env`, never hardcoded, never committed.

  Build the search-string generation and relevance-scoring agents behind a clean function
  interface (e.g. `generate_search_strings(jd_text)` and `score_relevance(jd_text, snippet)`),
  so the rest of the app never depends on provider-specific details and the model used can be
  changed later without touching other code.
- Serper is the search provider for now, kept behind its own module so it's easy to swap
  out later once a long-term search API is decided on.

## Interface Spec

### App shell / sidebar

Left sidebar, persistent across all pages, matching
the existing 10Pearls internal tools like the ATS dashboard, full height.

- **Top:** 10Pearls monogram/lettermark logo (use the real brand asset when available, the developer will provide so ask them, not
  a placeholder). Logo sits alone at the top; the wordmark appears on the landing page
  instead, not here.
- **Nav items, in order:**
  1. **Search** — the default/home view. Landing page with the JD input (see below).
  2. **Past searches** — history of previous searches: JD used, date, and a way to reopen
     the full ranked results for that search.
  3. **Starred profiles** — profiles the user has starred as good matches, aggregated
     across all searches (not scoped to a single JD). Lets a sourcer build a running list
     of promising candidates over time.
  4. **Recruited** *(scope to confirm, see Open Items below)* — a simple manual tag/marker
     on a starred profile indicating that person was actually hired from this pipeline.
     This is NOT meant to replicate full ATS functionality (stages, interviews, offers)
     since that already exists separately at 10Pearls. Keep this lightweight: a status flag
     and maybe a date, nothing more, unless told otherwise.
  5. **Admin panel** — placeholder for future settings (e.g. managing search API usage/
     quotas, user management once login exists). Low priority, build last.
- **Bottom of sidebar:** logged-in user's name and role (small avatar circle, name, role
  label), and a Log out action below it. This ties into the login/auth work planned for
  later. Until login exists, this can show placeholder/static text.

### Landing page ("Search")

This is the default view after login (or the default view for now, pre-login). Centered,
minimal, Google-search-style layout:

1. **10Pearls wordmark** (the real brand wordmark asset, not the monogram used in the
   sidebar, the developer will provide it please ask for it) — large, top of the centered block.
2. **"Talent Acquisition"** — small subtitle/tagline directly below the wordmark, muted
   color.
3. **Search bar** — a single rounded pill-shaped input, containing:
   - A **`+` upload icon** on the left — clicking it lets the user upload a JD PDF (reuses
     the existing `/jd/upload` endpoint).
   - A **text input** in the center — lets the user paste or type the JD directly instead
     of uploading (reuses the existing `/jd/text` endpoint). Placeholder text: "Paste a job
     description or upload a PDF".
   - A **platform dropdown** on the right side of the same bar — see below.
   - A **submit/search button** (circular, search icon) at the far right end of the bar.

### Platform dropdown

Sits inline inside the search bar, to the right of the text input, before the submit
button. Determines which `site:` restriction (if any) gets applied when generating the
X-ray search strings.

Options:
- **All sites** — no `site:` restriction; search strings can surface results from anywhere,
  including personal portfolio websites, not just the listed platforms.
- **LinkedIn** — restrict to `site:linkedin.com`
- **GitHub** — restrict to `site:github.com`
- **Upwork** — restrict to `site:upwork.com`
- **Fiverr** — restrict to `site:fiverr.com`
- **Behance** — restrict to `site:behance.net`

This selection should be passed to the search-string generation agent so it builds the
X-ray string with (or without) the corresponding `site:` operator, and should also be
stored alongside the search record in the database (see Database section) so past searches
show which platform scope was used.

### Open items from the interface spec

- **"Recruited" tab scope** — confirm whether this should stay as a lightweight manual tag
  (recommended) or needs to do more. Don't build beyond the lightweight version without
  explicit confirmation.
- **Real logo assets** — the monogram (sidebar) and wordmark (landing page) need to be
  swapped in from the actual 10Pearls brand files once available; do not ship a placeholder
  to production.

## Security requirements

This handles candidate personal data and will eventually sit behind a login, so build it
securely from the start, not as an afterthought:

- **No secrets in code.** All API keys (OpenAI, Serper, database credentials, Google OAuth
  credentials later) go in environment variables, never hardcoded, never committed. `.env`
  must be in `.gitignore`.
- **Input validation everywhere.** Validate file types and sizes on JD upload, sanitize any
  user-provided text before it's used in a database query or sent to an external API.
- **Parameterized queries only.** No raw string-interpolated SQL, use the ORM or
  parameterized queries to prevent SQL injection.
- **CORS locked down** to the actual frontend origin, not wildcard, even in development.
- **Rate limiting** on the search/generation endpoints, since they call paid third-party
  APIs, to prevent accidental or malicious runaway costs.
- **HTTPS assumed in production** — don't build anything that only works over plain HTTP.
- Plan the data model so that once login is added, every stored search can be tied to a
  `user_id`. Don't build the database schema in a way that assumes a single global user.

## Login (to be added later, but plan for it now)

We'll add a login page at the end of the project, not now. But:
- Design the Postgres schema with a `users` table and a `user_id` foreign key on the
  searches table from the start, even before login exists (it can default to a single
  placeholder user until then).
- Use a standard, well-supported auth approach when we get to it (e.g. session-based auth
  or JWT with a proper password hashing library like `bcrypt` or `argon2`). Don't roll
  custom crypto.

## Database (PostgreSQL)

We need to persist every search and its ranked results so past searches can be reviewed
later. Suggested schema to start from:

```sql
users (
  id, email, hashed_password, created_at
)

searches (
  id, user_id (FK), jd_text, jd_filename, search_strings (JSON),
  platform_scope,         -- "all", "linkedin", "github", "upwork", "fiverr", "behance"
  created_at
)

search_results (
  id, search_id (FK), url, title, snippet,
  original_position,      -- position as returned by the search API
  relevance_score,        -- score from Agent 2
  relevance_reasoning,    -- text explanation from Agent 2
  final_rank,             -- 1-10 after re-ranking
  is_starred,              -- true if the user starred this profile (Starred profiles page)
  is_recruited,            -- true if marked as hired (Recruited page, see Interface Spec)
  created_at
)
```

The "Past searches" sidebar page is just a list/detail view over the `searches` table
(and its related `search_results`), no extra schema needed. The "Starred profiles" page
queries `search_results` filtered to `is_starred = true` across all searches for the
current user, joined back to `searches` for JD context.

Use an ORM (SQLAlchemy is the natural fit with FastAPI) rather than raw SQL, and set up
Alembic for migrations from the start so schema changes are tracked properly.

## Export features (on the shortlist/ranking page)

Once the top-10 shortlist is shown, add buttons to export it for manual editing. All three
of the following are feasible:

1. **Download as Excel (.xlsx)** — generate the file server-side (e.g. with `openpyxl`) with
   columns: Name, URL, Relevance Score, Reasoning. Straightforward, no external auth needed.
2. **Download as CSV** — same data, simpler format. Easy, no dependencies beyond the
   standard library.
3. **Upload to Google Sheets** — this is significantly more involved. It requires Google
   OAuth: the user has to grant this app permission to write to their Google Sheets via the
   Google Sheets API. This means setting up a Google Cloud project, OAuth consent screen,
   and handling the OAuth flow (redirect, token storage, refresh tokens) on the backend.
   Build this as a separate, isolated module so it doesn't block the simpler Excel/CSV
   export from shipping first. Treat it as a stretch feature for a later phase.
4. **Push into an existing Excel file in OneDrive/SharePoint** — different from plain "download
   .xlsx" above. This is the Microsoft equivalent of the Google Sheets flow, and it's roughly
   the same complexity: it requires the Microsoft Graph API, an Azure AD (Entra ID) app
   registration, and the same shape of OAuth flow (consent, token storage, refresh tokens).
   Treat this the same as Google Sheets: a separate, isolated, later-phase module, not part
   of the initial build.

Build plain Excel (.xlsx) and CSV download first since they're simple, need no OAuth, and
unblock the "manual editing" need immediately. Google Sheets and OneDrive/Excel-online
upload are both real features worth having eventually, but both involve OAuth setup and
should follow once the core pipeline is stable, not be part of the first pass.

## Architecture reminders

- Keep the two LLM agents (search-string generation, relevance scoring) as separate,
  independently testable modules, not one big merged prompt.
- Keep the search provider (Serper) behind a single function/module so it can be swapped
  for a different provider later without touching the rest of the app.
- Keep the export logic (Excel/CSV/Sheets) as separate modules from the core ranking logic,
  so adding or changing an export format doesn't touch the pipeline itself.
