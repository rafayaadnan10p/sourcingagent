import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Star, UserCheck, ExternalLink } from 'lucide-react'
import { getStarred, toggleStar, toggleRecruit } from '../api/searches'
import type { SearchResult } from '../api/searches'
import { useToast } from '../context/ToastContext'

export default function StarredPage() {
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(true)

  const { showToast } = useToast()

  useEffect(() => {
    getStarred().then(setResults).finally(() => setLoading(false))
  }, [])

  const handleStar = async (result: SearchResult) => {
    const updated = await toggleStar(result.id)
    setResults((prev) => prev.map((r) => (r.id === updated.id ? updated : r)).filter((r) => r.is_starred))
    showToast('Unstarred')
  }

  const handleRecruit = async (result: SearchResult) => {
    const updated = await toggleRecruit(result.id)
    setResults((prev) => prev.map((r) => (r.id === updated.id ? updated : r)))
    showToast(updated.is_recruited ? '✓ Marked as recruited' : 'Removed from recruited')
  }

  if (loading) return (
    <div className="flex-1 overflow-y-auto p-8" style={{ backgroundColor: 'var(--bg)' }}>
      <div className="max-w-3xl mx-auto">
        <div className="h-7 w-44 shimmer rounded mb-6" />
        <div className="space-y-3">
          {[1,2,3].map(i => (
            <div key={i} className="bg-white rounded-2xl border border-gray-200 p-5 flex gap-3">
              <div className="flex-1 space-y-2">
                <div className="h-4 shimmer rounded w-1/2" />
                <div className="h-3 shimmer rounded w-1/3" />
                <div className="h-3 shimmer rounded w-full" />
                <div className="h-3 shimmer rounded w-4/5" />
              </div>
              <div className="flex flex-col gap-1">
                <div className="w-7 h-7 shimmer rounded-lg" />
                <div className="w-7 h-7 shimmer rounded-lg" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  return (
    <div className="flex-1 overflow-y-auto p-8" style={{ backgroundColor: 'var(--bg)' }}>
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center gap-2">
          <Star size={22} className="text-yellow-500" /> Starred Profiles
        </h1>

        {results.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="w-16 h-16 rounded-full bg-yellow-50 flex items-center justify-center mb-4">
              <Star size={28} className="text-yellow-300" />
            </div>
            <p className="text-base font-medium text-gray-600 mb-1">No starred profiles yet</p>
            <p className="text-sm text-gray-400 mb-4">Star candidates from the results page to build your shortlist here.</p>
            <Link to="/" className="text-sm font-medium text-blue-600 hover:underline">← Run a search</Link>
          </div>
        ) : (
          <div className="space-y-3">
            {results.map((result) => (
              <div key={result.id} className="bg-white rounded-2xl border border-gray-200 p-5 flex gap-3">
                <div className="flex-1 min-w-0">
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-base font-semibold text-blue-600 hover:underline flex items-center gap-1"
                  >
                    {result.title || result.url}
                    <ExternalLink size={13} className="shrink-0" />
                  </a>
                  <p className="text-sm text-gray-400 truncate mt-0.5">{result.url}</p>
                  {result.snippet && <p className="text-sm text-gray-600 mt-1 line-clamp-2">{result.snippet}</p>}
                  {result.relevance_reasoning && (
                    <p className="mt-2 text-sm text-gray-500 italic border-l-2 border-yellow-200 pl-3 leading-relaxed">{result.relevance_reasoning}</p>
                  )}
                </div>
                <div className="shrink-0 flex flex-col gap-1">
                  <button onClick={() => handleStar(result)} className="p-1.5 rounded-lg text-yellow-500 bg-yellow-50 hover:bg-yellow-100">
                    <Star size={16} fill="currentColor" />
                  </button>
                  <button
                    onClick={() => handleRecruit(result)}
                    className={`p-1.5 rounded-lg transition-colors ${result.is_recruited ? 'text-green-600 bg-green-50' : 'text-gray-400 hover:text-green-500 hover:bg-green-50'}`}
                  >
                    <UserCheck size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}



