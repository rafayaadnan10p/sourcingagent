import axios from 'axios'

// In dev: Vite proxy rewrites /api → localhost:8000
// In production: VITE_API_URL is set to the Render backend URL
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api',
  headers: { 'Content-Type': 'application/json' },
})

export default api

