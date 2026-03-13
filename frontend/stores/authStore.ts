import { create } from 'zustand'

/**
 * Interfaz para los datos del usuario autenticado
 */
interface User {
  id: string
  username: string
  displayName: string
  createdAt: Date
  lastLoginAt?: Date
}

/**
 * Estado de autenticación de la aplicación
 * 
 * Almacena:
 * - accessToken: JWT access token (solo en memoria, nunca en localStorage)
 * - user: Datos del usuario autenticado
 * 
 * El refresh token se almacena en httpOnly cookie (gestionado por backend)
 */
interface AuthState {
  accessToken: string | null
  user: User | null
  setAccessToken: (token: string) => void
  setUser: (user: User) => void
  logout: () => void
}

/**
 * Store de autenticación usando Zustand
 * 
 * Gestiona el estado de autenticación del usuario sin persistencia.
 * El access token se pierde al cerrar/refrescar la página (seguridad).
 * El refresh token en httpOnly cookie permite obtener nuevo access token.
 */
export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  
  /**
   * Almacena el access token JWT en memoria
   */
  setAccessToken: (token: string) => set({ accessToken: token }),
  
  /**
   * Almacena los datos del usuario autenticado
   */
  setUser: (user: User) => set({ user }),
  
  /**
   * Limpia el estado de autenticación (logout)
   * El refresh token se invalida en el backend
   */
  logout: () => set({ accessToken: null, user: null })
}))
