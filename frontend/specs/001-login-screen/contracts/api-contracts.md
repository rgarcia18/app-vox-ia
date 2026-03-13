# Contratos de API: Pantalla de Login

**Funcionalidad**: Pantalla de Login  
**Fecha**: 2026-03-07  
**Fase**: Phase 1 - Contratos de Interfaz

## Resumen

Este documento define los contratos de API entre el frontend (Next.js) y el backend de VoxIA para la funcionalidad de autenticación. Incluye endpoints, formatos de request/response, códigos de estado, y manejo de errores.

---

## Base URL

```
Desarrollo: http://localhost:8000
Producción: https://api.voxia.com
```

**Nota**: El frontend debe configurar la base URL mediante variable de entorno:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Endpoints de Autenticación

### 1. POST /api/auth/login

Autentica un usuario con credenciales (username + password) y retorna tokens JWT.

#### Request

**Headers**:
```
Content-Type: application/json
```

**Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Validación**:
- `username`: 3-50 caracteres, alfanumérico + `._@-`
- `password`: 6-100 caracteres

**Ejemplo**:
```json
{
  "username": "juan.perez",
  "password": "miPassword123"
}
```

#### Response - Éxito (200 OK)

**Headers**:
```
Content-Type: application/json
Set-Cookie: refresh_token=<JWT>; HttpOnly; Secure; SameSite=Strict; Max-Age=604800
```

**Body**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "juan.perez",
    "displayName": "Juan Pérez",
    "createdAt": "2026-01-15T10:30:00Z",
    "lastLoginAt": "2026-03-07T14:25:00Z"
  }
}
```

**Campos**:
- `access_token` (string): JWT access token válido por 15 minutos
- `user.id` (string): UUID del usuario
- `user.username` (string): Nombre de usuario
- `user.displayName` (string): Nombre para mostrar en UI
- `user.createdAt` (string): Fecha de creación (ISO 8601)
- `user.lastLoginAt` (string): Última fecha de login (ISO 8601)

**Cookie**:
- `refresh_token`: JWT refresh token válido por 7 días
- `HttpOnly`: No accesible desde JavaScript (seguridad XSS)
- `Secure`: Solo HTTPS en producción
- `SameSite=Strict`: Protección CSRF

#### Response - Credenciales Inválidas (401 Unauthorized)

```json
{
  "error": "invalid_credentials",
  "message": "Usuario o contraseña incorrectos"
}
```

**Manejo en Frontend**:
- Mostrar toast: "Usuario o contraseña incorrectos"
- Limpiar campo de password
- Devolver foco a campo de password
- Incrementar contador de intentos

#### Response - Rate Limiting (429 Too Many Requests)

```json
{
  "error": "too_many_requests",
  "message": "Demasiados intentos de login",
  "retry_after": 300
}
```

**Campos**:
- `retry_after` (number): Segundos hasta que se puede reintentar

**Manejo en Frontend**:
- Mostrar toast: "Demasiados intentos. Espera unos minutos"
- Deshabilitar formulario
- Mostrar countdown en botón
- Habilitar formulario cuando countdown llegue a 0

#### Response - Validación Fallida (422 Unprocessable Entity)

```json
{
  "error": "validation_error",
  "message": "Datos de entrada inválidos",
  "details": {
    "username": ["Mínimo 3 caracteres"],
    "password": ["Mínimo 6 caracteres"]
  }
}
```

**Manejo en Frontend**:
- Mostrar errores inline en campos correspondientes
- No debería ocurrir si validación de cliente funciona correctamente

#### Response - Error del Servidor (500 Internal Server Error)

```json
{
  "error": "internal_server_error",
  "message": "Error interno del servidor"
}
```

**Manejo en Frontend**:
- Mostrar toast: "No pudimos conectar con el servidor"
- Permitir reintento

---

### 2. POST /api/auth/refresh

Refresca el access token usando el refresh token almacenado en cookie httpOnly.

#### Request

**Headers**:
```
Cookie: refresh_token=<JWT>
```

**Body**: Ninguno (vacío)

**Nota**: El refresh token se envía automáticamente en la cookie, no en el body.

#### Response - Éxito (200 OK)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Campos**:
- `access_token` (string): Nuevo JWT access token válido por 15 minutos

**Manejo en Frontend**:
- Actualizar `accessToken` en Zustand
- Reintentar request original que falló con 401

#### Response - Refresh Token Inválido/Expirado (401 Unauthorized)

```json
{
  "error": "invalid_refresh_token",
  "message": "Sesión expirada"
}
```

**Manejo en Frontend**:
- Ejecutar logout automático
- Limpiar Zustand (accessToken, user)
- Redirect a `/` (login)

#### Response - Refresh Token No Presente (400 Bad Request)

```json
{
  "error": "missing_refresh_token",
  "message": "Token de refresco no encontrado"
}
```

**Manejo en Frontend**:
- Ejecutar logout automático
- Redirect a `/` (login)

---

### 3. POST /api/auth/logout

Invalida el refresh token y cierra la sesión del usuario.

#### Request

**Headers**:
```
Authorization: Bearer <access_token>
Cookie: refresh_token=<JWT>
```

**Body**: Ninguno (vacío)

#### Response - Éxito (200 OK)

```json
{
  "message": "Sesión cerrada exitosamente"
}
```

**Headers**:
```
Set-Cookie: refresh_token=; HttpOnly; Secure; SameSite=Strict; Max-Age=0
```

**Manejo en Frontend**:
- Limpiar Zustand (accessToken, user)
- Redirect a `/` (login)

#### Response - No Autenticado (401 Unauthorized)

```json
{
  "error": "unauthorized",
  "message": "No autenticado"
}
```

**Manejo en Frontend**:
- Limpiar Zustand de todas formas
- Redirect a `/` (login)

---

## Flujo de Autenticación Completo

```
┌─────────────────────────────────────────────────────────────┐
│              FLUJO DE AUTENTICACIÓN JWT                     │
└─────────────────────────────────────────────────────────────┘

1. Usuario ingresa credenciales
   ↓
2. Frontend: POST /api/auth/login
   {
     "username": "juan.perez",
     "password": "miPassword123"
   }
   ↓
3. Backend valida credenciales
   ├─ Válidas → Continuar
   └─ Inválidas → 401 Unauthorized
   ↓
4. Backend genera tokens
   ├─ access_token (15 min)
   └─ refresh_token (7 días)
   ↓
5. Backend responde 200 OK
   {
     "access_token": "...",
     "user": { ... }
   }
   Set-Cookie: refresh_token=...; HttpOnly
   ↓
6. Frontend almacena
   ├─ accessToken → Zustand (memoria)
   ├─ user → Zustand (memoria)
   └─ refreshToken → Cookie (automático)
   ↓
7. Frontend redirect a /dashboard
   ↓
8. Usuario usa aplicación
   Cada request incluye:
   Authorization: Bearer <access_token>
   ↓
9. Access token expira (15 min)
   Backend responde: 401 Unauthorized
   ↓
10. Interceptor Axios detecta 401
    ↓
11. Frontend: POST /api/auth/refresh
    Cookie: refresh_token=...
    ↓
12. Backend valida refresh token
    ├─ Válido → Nuevo access_token
    └─ Inválido → 401 Unauthorized → Logout
    ↓
13. Frontend actualiza accessToken en Zustand
    ↓
14. Frontend reintenta request original
    Authorization: Bearer <nuevo_access_token>
    ↓
15. Request exitoso → Usuario continúa
```

---

## Códigos de Estado HTTP

| Código | Significado | Uso |
|--------|-------------|-----|
| 200 | OK | Login exitoso, refresh exitoso, logout exitoso |
| 400 | Bad Request | Refresh token no presente |
| 401 | Unauthorized | Credenciales inválidas, refresh token inválido, no autenticado |
| 422 | Unprocessable Entity | Validación de datos fallida |
| 429 | Too Many Requests | Rate limiting activado |
| 500 | Internal Server Error | Error del servidor |
| 503 | Service Unavailable | Servidor temporalmente no disponible |

---

## Manejo de Errores en Frontend

### Interceptor Axios

```typescript
// services/api.ts
import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true // Importante para cookies httpOnly
})

// Request interceptor: Agregar access token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: Manejar refresh automático
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config

    // Si es 401 y no es el endpoint de refresh
    if (
      error.response?.status === 401 &&
      !original._retry &&
      !original.url?.includes('/auth/refresh')
    ) {
      original._retry = true

      try {
        // Intentar refresh
        const { data } = await api.post('/api/auth/refresh')
        
        // Actualizar token en store
        useAuthStore.getState().setAccessToken(data.access_token)
        
        // Actualizar header del request original
        original.headers.Authorization = `Bearer ${data.access_token}`
        
        // Reintentar request original
        return api(original)
      } catch (refreshError) {
        // Refresh falló → logout
        useAuthStore.getState().logout()
        window.location.href = '/'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default api
```

### Manejo de Errores por Tipo

```typescript
// components/shared/LoginForm.tsx
import { toast } from 'sonner'
import { AxiosError } from 'axios'

const handleLoginError = (error: unknown) => {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status
    const errorData = error.response?.data

    switch (status) {
      case 401:
        toast.error('Usuario o contraseña incorrectos')
        // Limpiar password, focus en password
        break

      case 429:
        const retryAfter = errorData?.retry_after || 300
        toast.warning('Demasiados intentos. Espera unos minutos')
        // Activar rate limiting con countdown
        break

      case 422:
        // Mostrar errores de validación inline
        const details = errorData?.details || {}
        // Actualizar estado de errores del formulario
        break

      case 500:
      case 503:
        toast.error('No pudimos conectar con el servidor')
        break

      default:
        toast.error('Ocurrió un error inesperado')
    }
  } else {
    // Error de red (sin respuesta del servidor)
    toast.error('No pudimos conectar con el servidor')
  }
}
```

---

## Seguridad

### Protección XSS
- ✅ Access token NUNCA en localStorage
- ✅ Access token solo en memoria (Zustand)
- ✅ Refresh token en httpOnly cookie (no accesible desde JS)

### Protección CSRF
- ✅ Refresh token con `SameSite=Strict`
- ✅ Validación de origen en backend
- ✅ CORS configurado correctamente

### Protección Brute Force
- ✅ Rate limiting en backend (429 después de N intentos)
- ✅ Countdown en frontend para evitar spam
- ✅ Mensajes de error genéricos (no revelar si username existe)

### HTTPS
- ✅ Cookies con flag `Secure` en producción
- ✅ Todas las comunicaciones sobre HTTPS en producción

---

## Variables de Entorno

```bash
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Backend
JWT_SECRET=<secret_key_segura>
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
RATE_LIMIT_MAX_ATTEMPTS=5
RATE_LIMIT_WINDOW_SECONDS=300
```

---

## Testing de Contratos

### Unit Tests (Frontend)

```typescript
// __tests__/unit/api.test.ts
describe('API Client', () => {
  it('debe agregar Authorization header con access token', async () => {
    useAuthStore.setState({ accessToken: 'test-token' })
    // Verificar que header se agrega correctamente
  })

  it('debe refrescar token automáticamente en 401', async () => {
    // Mock 401 response
    // Verificar que se llama /api/auth/refresh
    // Verificar que request original se reintenta
  })

  it('debe hacer logout si refresh falla', async () => {
    // Mock refresh failure
    // Verificar que se limpia store
    // Verificar redirect a /
  })
})
```

### Integration Tests (E2E)

```typescript
// __tests__/integration/auth-flow.spec.ts
test('flujo completo de autenticación', async ({ page }) => {
  // 1. Login exitoso
  await page.goto('/')
  await page.fill('[name="username"]', 'testuser')
  await page.fill('[name="password"]', 'testpass')
  await page.click('button[type="submit"]')
  await expect(page).toHaveURL('/dashboard')

  // 2. Verificar que requests incluyen token
  // 3. Simular expiración de access token
  // 4. Verificar refresh automático
  // 5. Logout
  // 6. Verificar redirect a login
})
```

---

## Próximos Pasos

1. ✅ Contratos de API definidos
2. → Generar `quickstart.md` (guía de desarrollo)
3. → Generar `tasks.md` (Phase 2 - comando separado)
