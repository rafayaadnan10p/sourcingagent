import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Clock, ChevronRight, Trash2, X, CheckSquare, Square } from 'lucide-react'
import { listSearches, deleteSearch } from '../api/searches'
import type { SearchSummary } from '../api/searches'

const PLATFORM_LABELS: Record<string, string> = {
  linkedin: 'LinkedIn', github: 'GitHub', upwork: 'Upwork',
  fiverr: 'Fiverr', behance: 'Behance', all: 'All Sites',
}

export default function PastSearchesPage() {
  const [searches, setSearches] = useState<SearchSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [selectionMode, setSelectionMode] = useState(false)
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [deleting, setDeleting] = useState(false)
  const [deletedMsg, setDeletedMsg] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    listSearches().then(setSearches).finally(() => setLoading(false))
  }, [])

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  const handleDeleteSelected = async () => {
    const count = selectedIds.size
    setDeleting(true)
    await Promise.all([...selectedIds].map((id) => deleteSearch(id)))
    setSearches((prev) => prev.filter((s) => !selectedIds.has(s.id)))
    setSelectedIds(new Set())
    setSelectionMode(false)
    setDeleting(false)
    setDeletedMsg(`${count} ${count === 1 ? 'search' : 'searches'} deleted`)
    setTimeout(() => setDeletedMsg(null), 3000)
  }

  const exitSelection = () => {
    setSelectionMode(false)
    setSelectedIds(new Set())
  }

  if (loading) return (
    <div className="flex-1 overflow-y-auto p-8" style={{ backgroundColor: 'var(--bg)' }}>
      <div className="max-w-3xl mx-auto">
        <div className="h-7 w-40 shimmer rounded mb-6" />
        <div className="space-y-3">
          {[1,2,3,4].map(i => (
            <div key={i} className="bg-white rounded-2xl border border-gray-200 p-5 flex items-center gap-4">
              <div className="flex-1 space-y-2">
                <div className="h-4 shimmer rounded w-2/3" />
                <div className="h-3 shimmer rounded w-1/3" />
              </div>
              <div className="w-4 h-4 shimmer rounded" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  return (
    <div className="flex-1 overflow-y-auto p-8" style={{ backgroundColor: 'var(--bg)' }}>
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-semibold text-gray-800 flex items-center gap-2">
            <Clock size={22} /> Past Searches
          </h1>
          {searches.length > 0 && (
            selectionMode ? (
              <button onClick={exitSelection} className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 transition-colors">
                <X size={15} /> Cancel
              </button>
            ) : (
              <button onClick={() => setSelectionMode(true)} className="text-gray-400 hover:text-red-500 transition-colors p-1.5 rounded-lg hover:bg-red-50" title="Select to delete">
                <Trash2 size={18} />
              </button>
            )
          )}
        </div>

        {deletedMsg && (
          <div className="mb-4 flex items-center gap-2 text-sm text-green-700 bg-green-50 border border-green-200 rounded-xl px-4 py-2.5">
            <CheckSquare size={15} className="shrink-0" /> {deletedMsg}
          </div>
        )}

        {searches.length === 0 ? (
          <p className="text-gray-400 text-sm">No searches yet. Run your first search from the Search page.</p>
        ) : (
          <div className="space-y-3">
            {searches.map((s) => (
              <div
                key={s.id}
                onClick={() => selectionMode ? toggleSelect(s.id) : navigate(`/results/${s.id}`, { state: { fromPastSearches: true } })}
                className={`w-full bg-white rounded-2xl border p-5 flex items-center gap-4 cursor-pointer transition-all text-left ${
                  selectionMode && selectedIds.has(s.id)
                    ? 'border-red-300 bg-red-50/40 shadow-sm'
                    : 'border-gray-200 hover:shadow-md'
                }`}
              >
                {/* Checkbox in selection mode */}
                {selectionMode && (
                  <div className="shrink-0 text-red-400">
                    {selectedIds.has(s.id) ? <CheckSquare size={20} /> : <Square size={20} className="text-gray-300" />}
                  </div>
                )}

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <p className="text-base font-semibold text-gray-800 truncate">{s.title}</p>
                    <span className={`shrink-0 text-xs font-medium px-2 py-0.5 rounded-full ${
                      s.platform_scope === 'linkedin' ? 'bg-blue-100 text-blue-700' :
                      s.platform_scope === 'github'   ? 'bg-gray-200 text-gray-800' :
                      s.platform_scope === 'upwork'   ? 'bg-emerald-100 text-emerald-700' :
                      s.platform_scope === 'fiverr'   ? 'bg-green-100 text-green-700' :
                      s.platform_scope === 'behance'  ? 'bg-purple-100 text-purple-700' :
                      'bg-gray-100 text-gray-600'
                    }`}>
                      {PLATFORM_LABELS[s.platform_scope] ?? s.platform_scope}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400">
                    {new Date(s.created_at).toLocaleString()} · {s.result_count} results
                  </p>
                </div>
                {!selectionMode && <ChevronRight size={16} className="text-gray-400 shrink-0" />}
              </div>
            ))}

            {/* Bulk delete action bar */}
            {selectionMode && selectedIds.size > 0 && (
              <div className="sticky bottom-4 flex items-center justify-between bg-[#1c1a17] text-white rounded-2xl px-5 py-3 shadow-xl">
                <span className="text-sm font-medium">{selectedIds.size} selected</span>
                <button
                  onClick={handleDeleteSelected}
                  disabled={deleting}
                  className="flex items-center gap-2 text-sm font-medium bg-red-500 hover:bg-red-600 disabled:opacity-60 transition-colors px-4 py-1.5 rounded-lg"
                >
                  <Trash2 size={14} />
                  {deleting ? 'Deleting…' : `Delete ${selectedIds.size}`}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}



