/**
 * Servicio de autenticación
 *
 * MODO ACTUAL: Mock local (sin backend)
 * Cuando el backend esté disponible, reemplazar la función `login` con:
 *
 *   import api from '@/services/api'
 *   export async function login(username: string, password: string) {
 *     const { data } = await api.post('/api/auth/login', { username, password })
 *     return data
 *   }
 *
 * Credenciales de prueba disponibles:
 *   - admin / password123   → login exitoso
 *   - cualquier otra combinación → error 401
 */

const MOCK_DELAY_MS = 800

const MOCK_USERS = [
  {
    username: 'admin',
    password: 'password123',
    user: {
      id: '550e8400-e29b-41d4-a716-446655440000',
      username: 'admin',
      displayName: 'Administrador VoxIA',
      createdAt: '2026-01-01T00:00:00Z',
      lastLoginAt: new Date().toISOString()
    }
  }
]

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
  // Simular latencia de red
  await new Promise(resolve => setTimeout(resolve, MOCK_DELAY_MS))

  const match = MOCK_USERS.find(
    u => u.username === username && u.password === password
  )

  if (!match) {
    // Lanzar error con la misma forma que Axios para que LoginForm lo maneje igual
    throw { response: { status: 401, data: { error: 'invalid_credentials' } } }
  }

  return {
    access_token: `mock-token-${Date.now()}`,
    user: match.user
  }
}
