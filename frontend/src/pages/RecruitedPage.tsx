import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { UserCheck, ExternalLink, Star } from 'lucide-react'
import { getStarred, toggleRecruit } from '../api/searches'
import type { SearchResult } from '../api/searches'
import { useToast } from '../context/ToastContext'

export default function RecruitedPage() {
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(true)

  const { showToast } = useToast()

  useEffect(() => {
    // Recruited profiles are a subset of starred — filter client-side
    getStarred().then((all) => {
      setResults(all.filter((r) => r.is_recruited))
    }).finally(() => setLoading(false))
  }, [])

  const handleRecruit = async (result: SearchResult) => {
    const updated = await toggleRecruit(result.id)
    setResults((prev) => prev.map((r) => (r.id === updated.id ? updated : r)).filter((r) => r.is_recruited))
    showToast('Removed from recruited')
  }

  if (loading) return (
    <div className="flex-1 overflow-y-auto p-8" style={{ backgroundColor: 'var(--bg)' }}>
      <div className="max-w-3xl mx-auto">
        <div className="h-7 w-32 shimmer rounded mb-6" />
        <div className="space-y-3">
          {[1,2,3].map(i => (
            <div key={i} className="bg-white rounded-2xl border border-gray-200 p-5 flex gap-3">
              <div className="w-9 h-9 shimmer rounded-full shrink-0" />
              <div className="flex-1 space-y-2">
                <div className="h-4 shimmer rounded w-1/2" />
                <div className="h-3 shimmer rounded w-1/3" />
                <div className="h-3 shimmer rounded w-full" />
              </div>
              <div className="w-20 h-6 shimmer rounded-full" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  return (
    <div className="flex-1 overflow-y-auto p-8" style={{ backgroundColor: 'var(--bg)' }}>
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-semibold text-gray-800 mb-2 flex items-center gap-2">
          <UserCheck size={22} className="text-green-600" /> Recruited
        </h1>
        <p className="text-sm text-gray-400 mb-6">
          Candidates manually marked as hired from this pipeline. Not a full ATS — just a lightweight tag.
        </p>

        {results.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="w-16 h-16 rounded-full bg-green-50 flex items-center justify-center mb-4">
              <UserCheck size={28} className="text-green-300" />
            </div>
            <p className="text-base font-medium text-gray-600 mb-1">No recruited profiles yet</p>
            <p className="text-sm text-gray-400 mb-4">Mark candidates as recruited from the results or starred page.</p>
            <Link to="/starred" className="text-sm font-medium text-blue-600 hover:underline">← View starred profiles</Link>
          </div>
        ) : (
          <div className="space-y-3">
            {results.map((result) => (
              <div key={result.id} className="bg-white rounded-2xl border border-gray-200 p-5 flex gap-3">
                <div className="w-9 h-9 rounded-full bg-green-100 flex items-center justify-center shrink-0">
                  <UserCheck size={17} className="text-green-600" />
                </div>
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
                </div>
                <div className="shrink-0 flex items-start gap-1">
                  <span className="text-sm bg-green-100 text-green-700 px-2.5 py-0.5 rounded-full font-medium">Recruited</span>
                  <button
                    onClick={() => handleRecruit(result)}
                    className="p-1.5 rounded-lg text-green-600 bg-green-50 hover:bg-red-50 hover:text-red-500 transition-colors"
                    title="Remove recruited tag"
                  >
                    <Star size={14} />
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



