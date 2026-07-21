import { Settings } from 'lucide-react'

export default function AdminPage() {
  return (
    <div className="flex-1 overflow-y-auto p-8" style={{ backgroundColor: 'var(--bg)' }}>
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-semibold text-gray-800 mb-2 flex items-center gap-2">
          <Settings size={22} /> Admin Panel
        </h1>
        <p className="text-sm text-gray-400 mb-6">Settings and configuration — coming in a future phase.</p>

        <div className="bg-white rounded-2xl border border-gray-200 p-8 text-center text-gray-400">
          <Settings size={44} className="mx-auto mb-3 opacity-30" />
          <p className="text-base text-gray-400">Admin features (API quota management, user management) will be added here.</p>
        </div>
      </div>
    </div>
  )
}



