import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { MsalProvider } from '@azure/msal-react'
import { msalInstance } from './auth/msalConfig'
import './index.css'
import App from './App.tsx'

// Initialise MSAL before rendering.
// When VITE_REQUIRE_AUTH is false the library is loaded but never triggers a login.
msalInstance.initialize().then(() => {
  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <MsalProvider instance={msalInstance}>
        <App />
      </MsalProvider>
    </StrictMode>,
  )
})


