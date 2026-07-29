import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react'
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

export default function App() {
  return (
    <ThemeProvider>
      <SearchProvider>
        <ToastProvider>
          <BrowserRouter>
            {REQUIRE_AUTH ? (
              <>
                <UnauthenticatedTemplate>
                  <LoginPage />
                </UnauthenticatedTemplate>
                <AuthenticatedTemplate>
                  <MainApp />
                </AuthenticatedTemplate>
              </>
            ) : (
              <MainApp />
            )}
          </BrowserRouter>
        </ToastProvider>
      </SearchProvider>
    </ThemeProvider>
  )
}


