# Guía de Backend: Autenticación VoxIA

**Para**: Agente/desarrollador de backend
**Contexto**: El frontend de VoxIA ya está implementado con mock local. Este documento describe los endpoints que debes implementar para que el frontend funcione con el backend real.

---

## Qué implementar

3 endpoints bajo el prefijo `/api/auth`:

| Método | Endpoint | Qué hace |
|--------|----------|----------|
| POST | `/api/auth/login` | Autentica usuario, retorna tokens |
| POST | `/api/auth/refresh` | Renueva el access token |
| POST | `/api/auth/logout` | Invalida la sesión |

---

## 1. POST `/api/auth/login`

### Request
```json
POST /api/auth/login
Content-Type: application/json

{
  "username": "juan.perez",
  "password": "miPassword123"
}
```

### Response exitosa `200 OK`
```json
// Body
{
  "access_token": "<JWT válido 15 minutos>",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "juan.perez",
    "displayName": "Juan Pérez",
    "createdAt": "2026-01-15T10:30:00Z",
    "lastLoginAt": "2026-03-07T14:25:00Z"
  }
}

// Header (el frontend lo maneja automáticamente como cookie)
Set-Cookie: refresh_token=<JWT válido 7 días>; HttpOnly; Secure; SameSite=Strict; Max-Age=604800
```

### Errores esperados

| Código | Cuándo | Body |
|--------|--------|------|
| `401` | Credenciales incorrectas | `{ "error": "invalid_credentials" }` |
| `429` | Demasiados intentos | `{ "error": "too_many_requests", "retry_after": 300 }` |
| `422` | Datos inválidos (formato) | `{ "error": "validation_error", "details": { ... } }` |

> **Importante**: Para 401, no indicar si fue el username o la password lo incorrecto (seguridad).

---

## 2. POST `/api/auth/refresh`

El refresh token llega automáticamente en la cookie, no en el body.

### Request
```
POST /api/auth/refresh
Cookie: refresh_token=<JWT>
```

### Response exitosa `200 OK`
```json
{
  "access_token": "<nuevo JWT válido 15 minutos>"
}
```

### Errores esperados

| Código | Cuándo | Body |
|--------|--------|------|
| `401` | Refresh token inválido o expirado | `{ "error": "invalid_refresh_token" }` |
| `400` | Cookie de refresh token ausente | `{ "error": "missing_refresh_token" }` |

---

## 3. POST `/api/auth/logout`

### Request
```
POST /api/auth/logout
Authorization: Bearer <access_token>
Cookie: refresh_token=<JWT>
```

### Response exitosa `200 OK`
```json
{ "message": "Sesión cerrada exitosamente" }

// Header: limpiar la cookie
Set-Cookie: refresh_token=; HttpOnly; Secure; SameSite=Strict; Max-Age=0
```

---

## Modelo de usuario en base de datos

```
User
├── id          UUID, primary key
├── username    string, único, case-insensitive, 3-50 chars, regex: /^[a-zA-Z0-9._@-]+$/
├── password    string, hash bcrypt
├── displayName string, 1-100 chars
├── createdAt   datetime
└── lastLoginAt datetime, nullable
```

> Los usuarios son **pre-creados por administradores**. No hay registro público.

---

## Tokens JWT

| Token | Duración | Almacenamiento |
|-------|----------|----------------|
| `access_token` | 15 minutos | Frontend: memoria (Zustand) |
| `refresh_token` | 7 días | Frontend: cookie httpOnly (backend la setea) |

---

## CORS

El frontend corre en `http://localhost:3000` (dev). Configura CORS para aceptar:
- `Origin: http://localhost:3000`
- `credentials: true` (necesario para las cookies httpOnly)

---

## Rate limiting sugerido

- Máximo **5 intentos fallidos** por IP en 5 minutos
- Responder `429` con `retry_after: 300` (segundos)

---

## Cómo conectar el frontend

Cuando el backend esté listo, en `services/authService.ts` cambiar el mock por:

```typescript
import api from '@/services/api'

export async function login(username: string, password: string) {
  const { data } = await api.post('/api/auth/login', { username, password })
  return data
}
```

La variable de entorno del frontend: `NEXT_PUBLIC_API_URL=http://localhost:8000`

---

## Referencia completa

Para más detalle (flujo completo, ejemplos de interceptores, tests): [`api-contracts.md`](./api-contracts.md)
