import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Plus, Loader2, Clock, MapPin, Building2, ChevronDown, X } from 'lucide-react'
import { runSearch, uploadJD, listSearches } from '../api/searches'
import type { SearchSummary } from '../api/searches'
import { useSearchContext } from '../context/SearchContext'
import { useTheme } from '../context/ThemeContext'
import AlertDialog from '../components/AlertDialog'
import wordmarkLight from '../assets/10pearls_wordmark.png'
import wordmarkDark from '../assets/10pearls_wordmark_white.png'

const PLATFORMS = [
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'github',   label: 'GitHub' },
  { value: 'upwork',   label: 'Upwork' },
  { value: 'fiverr',   label: 'Fiverr' },
  { value: 'behance',  label: 'Behance' },
  { value: 'all',      label: 'All Sites' },
]

const PLATFORM_LABELS: Record<string, string> = {
  linkedin: 'LinkedIn', github: 'GitHub', upwork: 'Upwork',
  fiverr: 'Fiverr', behance: 'Behance', all: 'All',
}

export default function SearchPage() {
  const [jdText, setJdText] = useState('')
  const [platform, setPlatform] = useState('linkedin')
  const [locationOverride, setLocationOverride] = useState('not_specified')
  const [companyChips, setCompanyChips] = useState<string[]>([])
  const [companyInput, setCompanyInput] = useState('')
  const [openToWork, setOpenToWork] = useState(false)
  const [loading, setLoading] = useState(false)
  const [progressStep, setProgressStep] = useState(0) // 0=idle 1=strings 2=search 3=scoring
  const [error, setError] = useState<string | null>(null)
  const [recentSearches, setRecentSearches] = useState<SearchSummary[]>([])
  const [isDragOver, setIsDragOver] = useState(false)
  const [validationError, setValidationError] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const navigate = useNavigate()
  const { setIsSearching } = useSearchContext()
  const { theme } = useTheme()
  const wordmark = theme === 'dark' ? wordmarkDark : wordmarkLight

  useEffect(() => {
    listSearches().then((all) => setRecentSearches(all.slice(0, 3))).catch(() => {})
    // Auto-focus the search bar on page load
    textareaRef.current?.focus()
  }, [])

  // Resize textarea whenever jdText changes (covers both typing and PDF extraction)
  useEffect(() => {
    const t = textareaRef.current
    if (t) {
      t.style.height = 'auto'
      t.style.height = Math.min(t.scrollHeight, 160) + 'px'
    }
  }, [jdText])

  const processFile = async (file: File) => {
    if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
      setError('Only PDF files are accepted.')
      return
    }
    try {
      const result = await uploadJD(file)
      setJdText(result.jd_text)
      setError(null)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err)
      setError(`PDF upload failed: ${msg}`)
    }
  }

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) await processFile(file)
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    const file = e.dataTransfer.files?.[0]
    if (file) await processFile(file)
  }

  const handleSubmit = async () => {
    if (!jdText.trim()) {
      setError('Please paste a job description or upload a PDF.')
      return
    }
    setLoading(true)
    setProgressStep(1)
    setIsSearching(true)
    setError(null)

    // Timed progress steps approximating real pipeline stages
    const t1 = setTimeout(() => setProgressStep(2), 5000)   // web search starts ~5s
    const t2 = setTimeout(() => setProgressStep(3), 11000)  // scoring starts ~11s

    try {
      const search = await runSearch(jdText.trim(), platform, locationOverride, companyChips.join(', '), openToWork)
      clearTimeout(t1); clearTimeout(t2)
      navigate(`/results/${search.id}`, { state: { search } })
    } catch (err: unknown) {
      clearTimeout(t1); clearTimeout(t2)
      const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } }
      if (axiosErr?.response?.status === 422 && axiosErr?.response?.data?.detail) {
        setValidationError(axiosErr.response.data.detail)
      } else {
        const msg = err instanceof Error ? err.message : 'Something went wrong.'
        setError(msg)
      }
    } finally {
      setLoading(false)
      setProgressStep(0)
      setIsSearching(false)
    }
  }

  return (
    <div className="flex flex-col items-center flex-1 min-h-screen px-6 pt-[12vh] pb-12" style={{ backgroundColor: 'var(--bg)' }}>
      {validationError && (
        <AlertDialog
          message={validationError}
          onClose={() => setValidationError(null)}
        />
      )}
      <div className="flex flex-col items-center w-full max-w-2xl">

        {/* Wordmark */}
        <div className="mb-2 flex flex-col items-center">
          <img src={wordmark} alt="10Pearls" className="h-40 mb-3 object-contain" />
          <p className="mt-2 text-lg font-bold tracking-tight" style={{ color: 'var(--text-primary)', fontSize: '1.375rem' }}>
            <span>AI-Powered Sourcing Agent</span>
            <span className="mx-3 inline-block" style={{ color: 'var(--text-muted)', fontSize: '1.6rem', lineHeight: 0, verticalAlign: 'middle' }}>&bull;</span>
            <span>Talent Acquisition</span>
          </p>
        </div>

        {/* Search bar */}
        <div
          className="w-full mt-4"
          onDragOver={(e) => { e.preventDefault(); setIsDragOver(true) }}
          onDragEnter={(e) => { e.preventDefault(); setIsDragOver(true) }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
        >
          <div className={`flex items-center bg-white rounded-2xl border shadow-sm transition-all px-2 py-1 gap-1 ${
            isDragOver ? 'border-blue-400 shadow-blue-100 shadow-md ring-2 ring-blue-100' : 'border-gray-300 hover:shadow-md'
          }`}>
            <button onClick={() => fileRef.current?.click()} className="w-9 h-9 flex items-center justify-center rounded-full text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors shrink-0" title="Upload JD as PDF">
              <Plus size={18} />
            </button>
            <input ref={fileRef} type="file" accept="application/pdf" className="hidden" onChange={handleUpload} />
            <textarea
              ref={textareaRef}
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              placeholder={isDragOver ? 'Drop PDF here…' : 'Paste a job description or upload a PDF'}
              rows={1}
              className="flex-1 resize-none outline-none text-sm text-gray-700 placeholder-gray-400 bg-transparent py-2 min-h-[36px] leading-relaxed"
            />
            <select value={platform} onChange={(e) => setPlatform(e.target.value)} className="text-xs text-gray-500 bg-transparent outline-none border-l border-gray-200 pl-2 pr-1 py-1 cursor-pointer">
              {PLATFORMS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
            </select>
            <button onClick={handleSubmit} disabled={loading} className="w-9 h-9 flex items-center justify-center rounded-full bg-[#1c1a17] text-white hover:bg-[#2c2926] disabled:opacity-50 transition-colors shrink-0 ml-1">
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
            </button>
          </div>
          {isDragOver && (
            <p className="mt-2 text-xs text-blue-500 text-center">Drop your PDF to extract the job description</p>
          )}
          {error && <p className="mt-3 text-sm text-red-500 text-center">{error}</p>}

          {/* Sourcing filters — same width as search bar */}
          <div className="mt-2 w-full flex items-stretch rounded-2xl border overflow-hidden" style={{ backgroundColor: 'var(--bg-filter)', borderColor: 'var(--border-sidebar)' }}>

            {/* Location */}
            <div className={`group relative flex items-center gap-2 px-4 py-3 flex-1 transition-colors cursor-pointer hover:bg-black/5 ${locationOverride !== 'not_specified' ? 'bg-blue-50/60' : ''}`}>
              <MapPin size={14} className={locationOverride !== 'not_specified' ? 'text-blue-500 shrink-0' : 'text-gray-400 shrink-0'} />
              <select
                value={locationOverride}
                onChange={(e) => setLocationOverride(e.target.value)}
                className="bg-transparent outline-none text-sm w-full cursor-pointer appearance-none pr-4"
                style={{ color: locationOverride !== 'not_specified' ? '#2563eb' : '#6b7280', paddingLeft: '2px' }}
              >
                <option value="not_specified" style={{ paddingLeft: '8px' }}>Location</option>
                <option value="Karachi" style={{ paddingLeft: '8px' }}>Karachi</option>
                <option value="Lahore" style={{ paddingLeft: '8px' }}>Lahore</option>
                <option value="Islamabad" style={{ paddingLeft: '8px' }}>Islamabad</option>
              </select>
              <ChevronDown size={13} className="absolute right-3 text-gray-400 pointer-events-none" />
              {locationOverride !== 'not_specified' && (
                <button onClick={(e) => { e.stopPropagation(); setLocationOverride('not_specified') }} className="absolute right-6 text-gray-400 hover:text-gray-600">
                  <X size={12} />
                </button>
              )}
            </div>

            {/* Subtle divider */}
            <div className="w-px self-stretch" style={{ backgroundColor: 'var(--border-sidebar)' }} />

            {/* Target companies — chip input */}
            <div className={`flex items-center gap-1.5 px-3 py-2 flex-[2] flex-wrap transition-colors hover:bg-black/5 ${companyChips.length > 0 ? 'bg-blue-50/60' : ''}`}>
              <Building2 size={14} className={companyChips.length > 0 ? 'text-blue-500 shrink-0' : 'text-gray-400 shrink-0'} />
              {/* Existing chips */}
              {companyChips.map((chip) => (
                <span key={chip} className="flex items-center gap-1 bg-white border border-gray-200 text-gray-700 text-xs px-2 py-0.5 rounded-full">
                  {chip}
                  <button onClick={() => setCompanyChips((prev) => prev.filter((c) => c !== chip))} className="text-gray-400 hover:text-red-400 transition-colors">
                    <X size={11} />
                  </button>
                </span>
              ))}
              {/* Text input */}
              <input
                type="text"
                value={companyInput}
                onChange={(e) => setCompanyInput(e.target.value)}
                onKeyDown={(e) => {
                  if ((e.key === 'Enter' || e.key === ',') && companyInput.trim()) {
                    e.preventDefault()
                    const val = companyInput.replace(/,$/, '').trim()
                    if (val && !companyChips.includes(val)) setCompanyChips((prev) => [...prev, val])
                    setCompanyInput('')
                  }
                  if (e.key === 'Backspace' && !companyInput && companyChips.length > 0) {
                    setCompanyChips((prev) => prev.slice(0, -1))
                  }
                }}
                placeholder={companyChips.length === 0 ? 'Specify company… e.g. Folio3, Systems' : ''}
                className="outline-none bg-transparent text-sm text-gray-700 placeholder-gray-400 min-w-[120px] flex-1"
              />
            </div>

            {/* Subtle divider */}
            {(platform === 'linkedin' || platform === 'all') && (
              <div className="w-px self-stretch" style={{ backgroundColor: 'var(--border-sidebar)' }} />
            )}
            {(platform === 'linkedin' || platform === 'all') && (
              <button
                onClick={() => setOpenToWork((v) => !v)}
                className={`flex items-center gap-2 px-5 py-3 text-sm font-medium transition-colors shrink-0 ${
                  openToWork
                    ? 'bg-green-50 text-green-700'
                    : 'text-gray-500 hover:text-green-600 hover:bg-green-50/60'
                }`}
              >
                <span className={`w-2 h-2 rounded-full shrink-0 transition-colors ${openToWork ? 'bg-green-500' : 'bg-gray-300'}`} />
                #OpenToWork
              </button>
            )}
          </div>
          {loading && (
            <div className="mt-5 w-full">
              <div className="w-full h-1 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-1000 ease-out"
                  style={{
                    width: progressStep === 1 ? '25%' : progressStep === 2 ? '55%' : '85%',
                    backgroundColor: '#1c1a17',
                  }}
                />
              </div>
              <p className="mt-2 text-xs text-gray-400 text-center">
                {progressStep === 1 && 'Generating search strings…'}
                {progressStep === 2 && 'Running web search…'}
                {progressStep === 3 && 'Scoring candidates…'}
              </p>
            </div>
          )}
        </div>

        {/* Recent searches — 3 hover cards */}
        {recentSearches.length > 0 && (
          <div className="mt-6 w-full grid grid-cols-3 gap-3">
            {recentSearches.map((s) => (
              <button
                key={s.id}
                onClick={() => navigate(`/results/${s.id}`)}
                className="group flex flex-col items-start px-4 py-4 rounded-2xl border border-gray-200 bg-white text-left transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5"
                style={{ minHeight: '100px' }}
              >
                {/* Platform badge ? always visible */}
                <span className="text-xs font-semibold px-2 py-0.5 rounded-md mb-2" style={{ backgroundColor: '#f0ede8', color: '#374151' }}>
                  {PLATFORM_LABELS[s.platform_scope] ?? s.platform_scope}
                </span>

                {/* Title ? always visible */}
                <p className="text-sm font-semibold text-gray-800 line-clamp-2 leading-snug">
                  {s.title}
                </p>

                {/* Divider + details — reveal on hover */}
                <div className="w-full mt-auto pt-3 border-t border-gray-100 opacity-0 group-hover:opacity-100 transition-opacity duration-200 mt-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-400 flex items-center gap-1">
                      <Clock size={11} />
                      {new Date(s.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}
                    </span>
                    <span className="text-xs text-gray-400">{s.result_count} results</span>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}




