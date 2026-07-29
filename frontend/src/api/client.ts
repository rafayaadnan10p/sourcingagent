import axios from 'axios'
import { getIdToken } from '../auth/msalConfig'

// In dev: Vite proxy rewrites /api → localhost:8000
// In production: VITE_API_URL is set to the backend URL
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Attach Microsoft Bearer token when auth is enabled
const REQUIRE_AUTH = import.meta.env.VITE_REQUIRE_AUTH === 'true'
if (REQUIRE_AUTH) {
  api.interceptors.request.use(async (config) => {
    const token = await getIdToken()
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  })
}

export default api

