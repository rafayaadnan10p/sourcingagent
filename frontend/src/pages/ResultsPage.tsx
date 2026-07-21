import { useEffect, useState, useRef } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import { Star, UserCheck, Download, ExternalLink, Copy, Check, ChevronDown, ChevronUp, ArrowLeft, RefreshCw, Link2 } from 'lucide-react'
import { getSearch, toggleStar, toggleRecruit, exportExcelUrl, exportCsvUrl, runSearch } from '../api/searches'
import type { Search, SearchResult } from '../api/searches'
import { extractSearchTitle } from '../utils/jdParser'
import { useToast } from '../context/ToastContext'

export default function ResultsPage() {
  const { id } = useParams<{ id: string }>()
  const location = useLocation()
  const navigate = useNavigate()
  const [search, setSearch] = useState<Search | null>(location.state?.search ?? null)
  const [loading, setLoading] = useState(!search)
  const [jdExpanded, setJdExpanded] = useState(false)
  const [openingTabs, setOpeningTabs] = useState(false)
  const [rerunConfirm, setRerunConfirm] = useState(false)
  const [rerunning, setRerunning] = useState(false)
  const [rerunProgress, setRerunProgress] = useState(0)
  const [linkCopied, setLinkCopied] = useState(false)
  const { showToast } = useToast()

  const handleOpenAllTabs = () => {
    if (!search) return
    const urls = search.results
      .filter((r) => r.final_rank !== null)
      .sort((a, b) => (a.final_rank ?? 0) - (b.final_rank ?? 0))
      .map((r) => r.url)

    if (urls.length > 10 && !window.confirm(`This will open ${urls.length} tabs at once. Continue?`)) return

    setOpeningTabs(true)
    urls.forEach((url, i) => setTimeout(() => window.open(url, '_blank'), i * 150))
    setTimeout(() => setOpeningTabs(false), urls.length * 150 + 500)
  }

  const handleCopyLink = () => {
    navigator.clipboard.writeText(window.location.href)
    setLinkCopied(true)
    showToast('Link copied to clipboard')
    setTimeout(() => setLinkCopied(false), 2000)
  }

  useEffect(() => {
    if (!search && id) {
      getSearch(id).then(setSearch).finally(() => setLoading(false))
    }
  }, [id, search])

  const handleStar = async (result: SearchResult) => {
    const updated = await toggleStar(result.id)
    setSearch((prev) =>
      prev ? { ...prev, results: prev.results.map((r) => (r.id === updated.id ? updated : r)) } : prev
    )
    showToast(updated.is_starred ? '⭐ Starred' : 'Unstarred')
  }

  const handleRecruit = async (result: SearchResult) => {
    const updated = await toggleRecruit(result.id)
    setSearch((prev) =>
      prev ? { ...prev, results: prev.results.map((r) => (r.id === updated.id ? updated : r)) } : prev
    )
    showToast(updated.is_recruited ? '✓ Marked as recruited' : 'Removed from recruited')
  }

  const handleRerun = async () => {
    if (!search) return
    setRerunning(true)
    setRerunConfirm(false)
    setRerunProgress(1)
    const t1 = setTimeout(() => setRerunProgress(2), 5000)
    const t2 = setTimeout(() => setRerunProgress(3), 11000)
    try {
      const newSearch = await runSearch(search.jd_text, search.platform_scope)
      clearTimeout(t1); clearTimeout(t2)
      navigate(`/results/${newSearch.id}`, { state: { search: newSearch } })
    } finally {
      setRerunning(false)
      setRerunProgress(0)
    }
  }

  if (loading) {
    return (
      <div className="flex-1 overflow-y-auto p-6" style={{ backgroundColor: 'var(--bg)' }}>
        <div className="max-w-5xl mx-auto">
          {/* Header skeleton */}
          <div className="mb-6">
            <div className="h-3 w-32 shimmer rounded mb-2" />
            <div className="h-5 w-2/3 shimmer rounded" />
          </div>
          {/* Export buttons skeleton */}
          <div className="flex gap-2 mb-6">
            {[1,2,3,4].map(i => <div key={i} className="h-9 w-36 shimmer rounded-lg" />)}
          </div>
          {/* Section label skeleton */}
          <div className="h-3 w-24 shimmer rounded mb-3" />
          {/* Result card skeletons */}
          <div className="space-y-3">
            {[1,2,3,4,5].map(i => (
              <div key={i} className="bg-white rounded-xl border border-gray-200 p-4 flex gap-4">
                <div className="w-8 h-8 rounded-full shimmer shrink-0" />
                <div className="flex-1 space-y-2">
                  <div className="flex justify-between gap-2">
                    <div className="h-4 shimmer rounded w-1/2" />
                    <div className="h-5 w-14 shimmer rounded-full shrink-0" />
                  </div>
                  <div className="h-3 shimmer rounded w-1/3" />
                  <div className="h-3 shimmer rounded w-full" />
                  <div className="h-3 shimmer rounded w-4/5" />
                </div>
                <div className="flex flex-col gap-1 shrink-0">
                  <div className="w-7 h-7 rounded-lg shimmer" />
                  <div className="w-7 h-7 rounded-lg shimmer" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (!search) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400">
        Search not found.
      </div>
    )
  }

  const shortlist = search.results.filter((r) => r.final_rank !== null).sort((a, b) => (a.final_rank ?? 0) - (b.final_rank ?? 0))
  const rest = search.results.filter((r) => r.final_rank === null)

  return (
    <div className="flex flex-1 h-full overflow-hidden" style={{ backgroundColor: 'var(--bg)' }}>

      {/* ── Left panel (30%) ─────────────────────────────────────────────── */}
      <div
        className="w-[30%] min-w-[240px] flex flex-col overflow-y-auto p-6 border-r shrink-0"
        style={{ borderColor: 'var(--border-sidebar)' }}
      >
        {/* Back to Past Searches */}
        <button
          onClick={() => navigate('/past-searches')}
          className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-700 transition-colors mb-5"
        >
          <ArrowLeft size={14} /> Past Searches
        </button>

        {/* Platform · timestamp */}
        <p className="text-sm text-gray-400 uppercase tracking-wide mb-2">
          {search.platform_scope} · {new Date(search.created_at).toLocaleString()}
        </p>

        {/* Job title */}
        <h1 className="text-lg font-semibold text-gray-800 leading-snug mb-4">
          {extractSearchTitle(search.jd_text)}
        </h1>

        {/* Re-run button — full width */}
        {rerunConfirm ? (
          <div className="flex flex-col gap-2 p-3 rounded-xl border mb-4" style={{ borderColor: 'var(--border-sidebar)', backgroundColor: 'var(--bg-card)' }}>
            <span className="text-sm text-gray-600 font-medium">Re-run this search?</span>
            <div className="flex gap-2">
              <button onClick={handleRerun} disabled={rerunning}
                className="flex-1 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 px-3 py-1.5 rounded-lg transition-colors">
                {rerunning ? 'Running…' : 'Yes, re-run'}
              </button>
              <button onClick={() => setRerunConfirm(false)}
                className="text-sm text-gray-500 hover:text-gray-700 px-3 py-1.5 rounded-lg hover:bg-gray-100 transition-colors">
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <button
            onClick={() => setRerunConfirm(true)}
            className="w-full flex items-center justify-center gap-2 text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 px-3 py-2 rounded-lg transition-colors mb-4"
          >
            <RefreshCw size={14} /> Re-run search
          </button>
        )}

        {/* Divider */}
        <div className="h-px mb-4" style={{ backgroundColor: 'var(--border-sidebar)' }} />

        {/* Job Description collapsible */}
        <button
          onClick={() => setJdExpanded((v) => !v)}
          className="flex items-center justify-between w-full text-sm font-medium text-gray-700 mb-2 hover:text-gray-900 transition-colors"
        >
          <span>Job Description</span>
          {jdExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
        {jdExpanded && (
          <div className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap overflow-y-auto max-h-[55vh]">
            {search.jd_text.replace(/\*{1,3}/g, '')}
          </div>
        )}
      </div>

      {/* ── Right panel (70%) ────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto p-6 relative">

        {/* Re-run progress overlay */}
        {rerunning && (
          <div className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-4" style={{ backgroundColor: 'var(--bg)', opacity: 0.95 }}>
            <div className="w-64">
              <div className="w-full h-1 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full rounded-full transition-all duration-1000 ease-out" style={{ width: rerunProgress === 1 ? '25%' : rerunProgress === 2 ? '55%' : '85%', backgroundColor: 'var(--accent)' }} />
              </div>
              <p className="mt-3 text-sm text-center" style={{ color: 'var(--text-muted)' }}>
                {rerunProgress === 1 && 'Generating search strings…'}
                {rerunProgress === 2 && 'Running web search…'}
                {rerunProgress === 3 && 'Scoring candidates…'}
              </p>
            </div>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex flex-wrap gap-2 mb-5 items-center">
          <button
            onClick={handleOpenAllTabs}
            disabled={openingTabs}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg disabled:opacity-60 transition-opacity"
            style={{ backgroundColor: 'var(--accent)', color: 'var(--bg)', border: '1px solid var(--border-sidebar)' }}
            onMouseEnter={e => (e.currentTarget.style.opacity = '0.85')}
            onMouseLeave={e => (e.currentTarget.style.opacity = '1')}
          >
            <ExternalLink size={15} />
            {openingTabs ? 'Opening…' : 'Open all in new tab'}
          </button>
          <DropdownButton
            label={<><Download size={15} /> Download</>}
            className="border border-gray-300 bg-white hover:bg-gray-50 text-gray-700"
            items={[
              { label: 'Download as .xlsx', href: exportExcelUrl(search.id) },
              { label: 'Download as .csv',  href: exportCsvUrl(search.id) },
            ]}
          />
          <DropdownButton
            label={<><ExternalLink size={15} /> Open in</>}
            className="border border-gray-200 bg-white hover:bg-gray-50 text-gray-400"
            items={[
              { label: 'MS Excel (browser)', disabled: true },
              { label: 'Google Sheets',      disabled: true },
            ]}
          />
          {/* Copy link */}
          <button
            onClick={handleCopyLink}
            title="Copy link to this search"
            className="flex items-center gap-1.5 px-3 py-2 text-sm rounded-lg border transition-colors"
            style={{ borderColor: 'var(--border-sidebar)', color: linkCopied ? '#16a34a' : 'var(--text-muted)', backgroundColor: 'var(--bg-card)' }}
          >
            {linkCopied ? <Check size={14} /> : <Link2 size={14} />}
            {linkCopied ? 'Copied!' : 'Copy link'}
          </button>
        </div>

        {/* Shortlist label */}
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
          Top {shortlist.length} Shortlist
        </h2>

        {/* Empty state */}
        {shortlist.length === 0 && rest.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="w-14 h-14 rounded-full flex items-center justify-center mb-4" style={{ backgroundColor: 'var(--bg-filter)' }}>
              <ExternalLink size={24} style={{ color: 'var(--text-muted)' }} />
            </div>
            <p className="text-base font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>No results found</p>
            <p className="text-sm mb-4" style={{ color: 'var(--text-muted)' }}>Try re-running the search or adjusting the JD with more specific role details.</p>
            <button onClick={() => setRerunConfirm(true)} className="text-sm font-medium text-blue-600 hover:underline flex items-center gap-1">
              <RefreshCw size={13} /> Re-run search
            </button>
          </div>
        )}
        <div className="space-y-3 mb-8">
          {shortlist.map((result) => (
            <ResultCard
              key={result.id}
              result={result}
              onStar={handleStar}
              onRecruit={handleRecruit}
            />
          ))}
        </div>

        {/* Below-shortlist section */}
        {rest.length > 0 && (
          <>
            <div className="flex items-center gap-3 my-6">
              <div className="flex-1 h-px bg-gray-200" />
              <span className="text-xs font-medium text-gray-400 uppercase tracking-widest">Below shortlist</span>
              <div className="flex-1 h-px bg-gray-200" />
            </div>
            <div className="space-y-2">
              {rest.map((result) => (
                <ResultCard
                  key={result.id}
                  result={result}
                  onStar={handleStar}
                  onRecruit={handleRecruit}
                  compact
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

// ── Dropdown button ────────────────────────────────────────────────────────
function DropdownButton({
  label,
  items,
  className = '',
}: {
  label: React.ReactNode
  className?: string
  items: { label: string; href?: string; disabled?: boolean }[]
}) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((v) => !v)}
        className={`flex items-center gap-2 px-4 py-2 text-sm rounded-lg transition-colors ${className}`}
      >
        {label}
        <ChevronDown size={13} className={`transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && (
        <div className="absolute left-0 top-full mt-1 w-48 bg-white border border-gray-200 rounded-xl shadow-lg z-20 overflow-hidden">
          {items.map((item) =>
            item.disabled ? (
              <div key={item.label} className="flex items-center justify-between px-4 py-2.5 text-sm text-gray-400 cursor-not-allowed">
                {item.label}
                <span className="text-xs bg-gray-100 text-gray-400 px-1.5 py-0.5 rounded">Soon</span>
              </div>
            ) : (
              <a
                key={item.label}
                href={item.href}
                onClick={() => setOpen(false)}
                className="block px-4 py-2.5 text-sm text-gray-700 hover:bg-transparent transition-colors"
              >
                {item.label}
              </a>
            )
          )}
        </div>
      )}
    </div>
  )
}

function ResultCard({
  result,
  onStar,
  onRecruit,
  compact = false,
}: {
  result: SearchResult
  onStar: (r: SearchResult) => void
  onRecruit: (r: SearchResult) => void
  compact?: boolean
}) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(result.url)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  const cardBg =
    result.relevance_score === null ? 'bg-white'
    : result.relevance_score >= 8   ? 'bg-green-50'
    : result.relevance_score >= 6   ? 'bg-yellow-50'
    : 'bg-red-50'

  const cardBorder =
    result.relevance_score === null ? 'border-gray-200'
    : result.relevance_score >= 8   ? 'border-green-200'
    : result.relevance_score >= 6   ? 'border-yellow-200'
    : 'border-red-200'

  return (
    <div className={`${cardBg} ${cardBorder} rounded-2xl border p-5 flex gap-4 ${compact ? 'opacity-60' : ''}`}>
      {/* Rank badge */}
      {result.final_rank && (
        <div className="shrink-0 w-9 h-9 rounded-full bg-[#1c1a17] text-white text-sm font-bold flex items-center justify-center">
          {result.final_rank}
        </div>
      )}

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <a
            href={result.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-base font-semibold text-blue-600 hover:underline truncate"
          >
            {result.title || result.url}
          </a>
          {result.relevance_score !== null && (
            <div className="shrink-0 flex flex-col items-end gap-1">
              <span className={`text-sm font-semibold px-2.5 py-0.5 rounded-full ${
                result.relevance_score >= 8 ? 'bg-green-100 text-green-700' :
                result.relevance_score >= 6 ? 'bg-yellow-100 text-yellow-700' :
                'bg-red-100 text-red-600'
              }`}>
                {result.relevance_score}/10
              </span>
              <div className="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${
                    result.relevance_score >= 8 ? 'bg-green-400' :
                    result.relevance_score >= 6 ? 'bg-yellow-400' :
                    'bg-red-400'
                  }`}
                  style={{ width: `${(result.relevance_score / 10) * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>
        <div className="flex items-center gap-1.5 mb-1">
          <p className="text-sm text-gray-400 truncate">{result.url}</p>
          <button
            onClick={handleCopy}
            title="Copy URL"
            className={`shrink-0 p-0.5 rounded transition-colors ${
              copied ? 'text-green-600' : 'text-gray-400 hover:text-gray-500'
            }`}
          >
            {copied ? <Check size={12} /> : <Copy size={12} />}
          </button>
        </div>
        {result.snippet && (
          <p className="text-sm text-gray-600 line-clamp-2 mt-1">{result.snippet}</p>
        )}
        {result.relevance_reasoning && !compact && (
          <p className="mt-2 text-sm text-gray-500 italic border-l-2 border-gray-200 pl-3 leading-relaxed">
            {result.relevance_reasoning}
          </p>
        )}
      </div>

      {/* Actions */}
      <div className="shrink-0 flex flex-col gap-1">
        <button
          onClick={() => onStar(result)}
          title={result.is_starred ? 'Unstar' : 'Star'}
          className={`p-1.5 rounded-lg transition-colors ${
            result.is_starred ? 'text-yellow-500 bg-yellow-50' : 'text-gray-400 hover:text-yellow-400 hover:bg-yellow-50'
          }`}
        >
          <Star size={16} fill={result.is_starred ? 'currentColor' : 'none'} />
        </button>
        <button
          onClick={() => onRecruit(result)}
          title={result.is_recruited ? 'Mark as not recruited' : 'Mark as recruited'}
          className={`p-1.5 rounded-lg transition-colors ${
            result.is_recruited ? 'text-green-600 bg-green-50' : 'text-gray-400 hover:text-green-500 hover:bg-green-50'
          }`}
        >
          <UserCheck size={16} />
        </button>
      </div>
    </div>
  )
}




