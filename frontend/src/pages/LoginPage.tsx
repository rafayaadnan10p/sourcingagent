import { useMsal } from '@azure/msal-react'
import { loginRequest } from '../auth/msalConfig'
import { useTheme } from '../context/ThemeContext'
import wordmarkLight from '../assets/10pearls_wordmark.png'
import wordmarkDark from '../assets/10pearls_wordmark_white.png'

export default function LoginPage() {
  const { instance } = useMsal()
  const { theme } = useTheme()
  const wordmark = theme === 'dark' ? wordmarkDark : wordmarkLight

  const handleLogin = () => {
    instance.loginRedirect(loginRequest)
  }

  return (
    <div
      className="flex flex-col items-center justify-center min-h-screen px-6"
      style={{ backgroundColor: 'var(--bg)' }}
    >
      <div className="flex flex-col items-center gap-8 w-full max-w-sm">
        {/* 10Pearls wordmark */}
        <div className="flex flex-col items-center gap-2">
          <img src={wordmark} alt="10Pearls" className="h-32 object-contain" />
          <p className="text-lg font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>
            AI-Powered Sourcing Agent
          </p>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            Talent Acquisition
          </p>
        </div>

        {/* Sign in card */}
        <div
          className="w-full rounded-2xl border p-8 flex flex-col items-center gap-5 shadow-sm"
          style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-sidebar)' }}
        >
          <p className="text-base font-medium text-center" style={{ color: 'var(--text-secondary)' }}>
            Sign in with your 10Pearls account to continue
          </p>

          {/* Microsoft sign-in button — follows Microsoft brand guidelines */}
          <button
            onClick={handleLogin}
            className="w-full flex items-center justify-center gap-3 px-5 py-3 rounded-lg border border-gray-300 bg-white hover:bg-gray-50 transition-colors shadow-sm"
          >
            {/* Microsoft logo SVG */}
            <svg width="20" height="20" viewBox="0 0 21 21" xmlns="http://www.w3.org/2000/svg">
              <rect x="1"  y="1"  width="9" height="9" fill="#F25022" />
              <rect x="11" y="1"  width="9" height="9" fill="#7FBA00" />
              <rect x="1"  y="11" width="9" height="9" fill="#00A4EF" />
              <rect x="11" y="11" width="9" height="9" fill="#FFB900" />
            </svg>
            <span className="text-sm font-semibold text-gray-700">Sign in with Microsoft</span>
          </button>
        </div>
      </div>
    </div>
  )
}
