import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import { ToastProvider } from './context/ToastContext'
import { SearchProvider } from './context/SearchContext'
import Sidebar from './components/Sidebar'
import ThemeToggle from './components/ThemeToggle'
import SearchPage from './pages/SearchPage'
import ResultsPage from './pages/ResultsPage'
import PastSearchesPage from './pages/PastSearchesPage'
import StarredPage from './pages/StarredPage'
import RecruitedPage from './pages/RecruitedPage'
import AdminPage from './pages/AdminPage'
import LoginPage from './pages/LoginPage'
import api from './api/client'
import './index.css'

const REQUIRE_AUTH = import.meta.env.VITE_REQUIRE_AUTH === 'true'

function MainApp() {
  return (
    <div className="flex h-screen overflow-hidden" style={{ backgroundColor: 'var(--bg)' }}>
      <Sidebar />
      <main className="flex flex-1 min-w-0 overflow-hidden relative">
        <ThemeToggle />
        <Routes>
          <Route path="/"                element={<SearchPage />} />
          <Route path="/results/:id"     element={<ResultsPage />} />
          <Route path="/past-searches"   element={<PastSearchesPage />} />
          <Route path="/starred"         element={<StarredPage />} />
          <Route path="/recruited"       element={<RecruitedPage />} />
          <Route path="/admin"           element={<AdminPage />} />
        </Routes>
      </main>
    </div>
  )
}

function AuthGate({ children }: { children: React.ReactNode }) {
  const [checked, setChecked] = useState(false)
  const [loggedIn, setLoggedIn] = useState(false)

  useEffect(() => {
    api.get('/auth/me')
      .then(() => setLoggedIn(true))
      .catch(() => setLoggedIn(false))
      .finally(() => setChecked(true))
  }, [])

  if (!checked) return null
  if (!loggedIn) return <LoginPage />
  return <>{children}</>
}

export default function App() {
  return (
    <ThemeProvider>
      <SearchProvider>
        <ToastProvider>
          <BrowserRouter>
            {REQUIRE_AUTH ? (
              <AuthGate>
                <MainApp />
              </AuthGate>
            ) : (
              <MainApp />
            )}
          </BrowserRouter>
        </ToastProvider>
      </SearchProvider>
    </ThemeProvider>
  )
}


