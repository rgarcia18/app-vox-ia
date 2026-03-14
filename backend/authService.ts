'use client'

import api from '@/services/api'

/**
 * Servicio de autenticación — conectado al backend real (FastAPI)
 * 
 * Para volver al mock local, descomentar la sección MOCK
 * y comentar la sección REAL BACKEND.
 */

// =====================
// REAL BACKEND
// =====================
export async function login(username: string, password: string) {
  const { data } = await api.post('/api/auth/login', { username, password })
  // data = { access_token, user: { id, username, displayName, createdAt, lastLoginAt } }
  return data
}

export async function logout() {
  try {
    await api.post('/api/auth/logout')
  } catch {
    // Ignorar errores en logout — igual limpiamos sesión local
  }
}

export async function refreshToken() {
  const { data } = await api.post('/api/auth/refresh')
  return data.access_token
}

// =====================
// MOCK LOCAL (para desarrollo sin backend)
// Descomentar si necesitas probar sin el servidor Python
// =====================
// const MOCK_USER = {
//   id: 'mock-001',
//   username: 'admin',
//   displayName: 'Administrador VoxIA',
//   createdAt: new Date().toISOString(),
//   lastLoginAt: new Date().toISOString(),
// }
//
// export async function login(username: string, password: string) {
//   await new Promise(r => setTimeout(r, 800))
//   if (username === 'admin' && password === 'password123') {
//     return { access_token: 'mock-token-123', user: MOCK_USER }
//   }
//   throw { response: { status: 401, data: { error: 'invalid_credentials' } } }
// }
//
// export async function logout() {}
// export async function refreshToken() { return 'mock-token-refreshed' }
