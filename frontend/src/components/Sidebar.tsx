import { useState, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import { Search, Clock, Star, UserCheck, Settings, LogOut } from 'lucide-react'
import { useSearchContext } from '../context/SearchContext'
import { useTheme } from '../context/ThemeContext'
import monogramLight from '../assets/10pearls_monogram.png'
import monogramDark from '../assets/10pearls_monogram_white.png'
import api from '../api/client'

const REQUIRE_AUTH = import.meta.env.VITE_REQUIRE_AUTH === 'true'

const navItems = [
  { to: '/',               icon: Search,    label: 'Search' },
  { to: '/past-searches',  icon: Clock,     label: 'Past Searches' },
  { to: '/starred',        icon: Star,      label: 'Starred Profiles' },
  { to: '/recruited',      icon: UserCheck, label: 'Recruited' },
  { to: '/admin',          icon: Settings,  label: 'Admin' },
]

export default function Sidebar() {
  const { isSearching } = useSearchContext()
  const { theme } = useTheme()
  const monogram = theme === 'dark' ? monogramDark : monogramLight
  const [userEmail, setUserEmail] = useState<string>('')

  useEffect(() => {
    if (!REQUIRE_AUTH) return
    api.get('/auth/me').then(r => setUserEmail(r.data.email)).catch(() => {})
  }, [])

  const initial = userEmail ? userEmail[0].toUpperCase() : 'HR'
  const displayEmail = userEmail || 'HR Sourcer'

  const handleLogout = () => {
    window.location.href = '/auth/logout'
  }

  return (
    <aside className="flex flex-col h-screen w-[72px] hover:w-60 transition-all duration-200 overflow-hidden shrink-0 group" style={{ backgroundColor: 'var(--bg-sidebar)', color: 'var(--text-primary)' }}>

      {/* Logo / monogram — click takes you home */}
      <NavLink to="/" className="flex items-center h-16 border-b hover:bg-black/5 dark:hover:bg-white/5 transition-colors px-0" style={{ borderColor: 'var(--border-sidebar)' }}>
        <div className="w-[72px] flex items-center justify-center shrink-0">
          <img src={monogram} alt="10Pearls" className="w-9 h-9 object-contain" />
        </div>
        <span className="font-semibold text-sm whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 text-gray-900 pr-4">
          Talent Acquisition
        </span>
      </NavLink>

      {/* Nav items */}
      <nav className="flex-1 py-4">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center pl-[22px] pr-4 py-3 gap-3 text-sm transition-colors duration-150 whitespace-nowrap
               ${isActive
                ? 'bg-black/10 dark:bg-white/10 text-gray-900 font-semibold'
                : 'text-gray-500 hover:bg-black/5 dark:hover:bg-white/5 hover:text-gray-800'
              }`
            }
          >
            <div className="relative shrink-0">
              <Icon size={18} />
              {to === '/' && isSearching && (
                <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
              )}
            </div>
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 pr-4 text-left">
              {label}
            </span>
          </NavLink>
        ))}
      </nav>

      {/* User / logout */}
      <div className="border-t" style={{ borderColor: 'var(--border-sidebar)' }}>
        <div className="flex items-center pl-[22px] pr-4 py-3 gap-3">
          <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center shrink-0">
            <span className="text-white text-xs font-bold">{initial}</span>
          </div>
          <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 min-w-0 flex-1">
            <p className="text-xs font-medium text-gray-800 truncate">{displayEmail}</p>
            <p className="text-xs text-gray-500 truncate">Talent Acquisition</p>
          </div>
          {REQUIRE_AUTH && (
            <button
              onClick={handleLogout}
              title="Sign out"
              className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 shrink-0 text-gray-400 hover:text-red-500 transition-colors"
            >
              <LogOut size={15} />
            </button>
          )}
        </div>
      </div>
    </aside>
  )
}



