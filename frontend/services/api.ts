import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

/**
 * Cliente Axios configurado para la API de VoxIA
 * 
 * Características:
 * - Base URL desde variable de entorno
 * - Soporte para cookies httpOnly (withCredentials)
 * - Interceptor de request: agrega Authorization header automáticamente
 * - Interceptor de response: refresh automático de token en 401
 */
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true // Importante para enviar/recibir cookies httpOnly
})

/**
 * Request interceptor: Agrega access token a cada request
 * 
 * Si existe un access token en el store, lo agrega al header Authorization.
 * El backend valida este token para autorizar las operaciones.
 */
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/**
 * Response interceptor: Maneja refresh automático de token
 * 
 * Cuando el backend responde 401 (token expirado):
 * 1. Intenta refrescar el token usando el refresh token (httpOnly cookie)
 * 2. Si el refresh es exitoso, actualiza el access token y reintenta el request original
 * 3. Si el refresh falla, hace logout y redirige al login
 * 
 * Esto permite que la sesión se mantenga activa sin intervención del usuario.
 */
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Si es 401 y no es el endpoint de refresh y no hemos reintentado
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/refresh')
    ) {
      originalRequest._retry = true

      try {
        // Intentar refresh del token
        const { data } = await api.post('/api/auth/refresh')
        
        // Actualizar access token en el store
        useAuthStore.getState().setAccessToken(data.access_token)
        
        // Actualizar header del request original con el nuevo token
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`
        
        // Reintentar el request original
        return api(originalRequest)
      } catch (refreshError) {
        // Refresh falló - sesión expirada completamente
        useAuthStore.getState().logout()
        
        // Redirigir al login solo si estamos en el navegador
        if (typeof window !== 'undefined') {
          window.location.href = '/'
        }
        
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default api
