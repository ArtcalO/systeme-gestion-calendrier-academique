import axios from 'axios'
import { ElMessage } from 'element-plus'

const instance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
})

// Request interceptor - attach JWT token
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle errors & token refresh
instance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        try {
          const res = await axios.post('/api/v1/auth/refresh/', { refresh: refreshToken })
          const newAccess = res.data.access
          localStorage.setItem('access_token', newAccess)
          originalRequest.headers.Authorization = `Bearer ${newAccess}`
          return instance(originalRequest)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      } else {
        window.location.href = '/login'
      }
    }

    const msg = error.response?.data?.detail
      || error.response?.data?.error
      || error.response?.data?.message
      || 'Une erreur est survenue'

    if (error.response?.status !== 401) {
      ElMessage.error(typeof msg === 'object' ? JSON.stringify(msg) : msg)
    }

    return Promise.reject(error)
  }
)

export default instance
