import { useTheme } from '../context/ThemeContext'

// Minimal vector sun icon
const SunIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
    <circle cx="12" cy="12" r="4"/>
    <line x1="12" y1="2" x2="12" y2="4"/>
    <line x1="12" y1="20" x2="12" y2="22"/>
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
    <line x1="2" y1="12" x2="4" y2="12"/>
    <line x1="20" y1="12" x2="22" y2="12"/>
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
  </svg>
)

// Minimal vector crescent moon icon
const MoonIcon = () => (
  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
  </svg>
)

export default function ThemeToggle() {
  const { theme, toggle } = useTheme()
  const isDark = theme === 'dark'

  return (
    <button
      onClick={toggle}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      className="fixed top-4 z-50 rounded-full transition-all duration-300"
      style={{
        right: '20px',
        width: '52px',
        height: '28px',
        backgroundColor: isDark ? '#4a4745' : '#d9d6d0',
        border: '1px solid',
        borderColor: isDark ? '#5a5754' : '#b0aba3',
      }}
    >
      {/* Sliding circle */}
      <span
        className="absolute rounded-full shadow-sm transition-all duration-300 flex items-center justify-center"
        style={{
          width: '22px',
          height: '22px',
          backgroundColor: isDark ? '#ede9e3' : '#ffffff',
          color: isDark ? '#2d2b28' : '#4a4745',
          left: isDark ? '27px' : '2px',
          top: '2px',
        }}
      >
        {isDark ? <MoonIcon /> : <SunIcon />}
      </span>
    </button>
  )
}



