/**
 * Servicio de autenticación — conectado al backend real
 */
import api from '@/services/api'

export interface AuthUser {
  id: string
  username: string
  displayName: string
  createdAt: string
  lastLoginAt: string
}

export interface LoginResponse {
  access_token: string
  user: AuthUser
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>('/api/auth/login', { username, password })
  return data
}
