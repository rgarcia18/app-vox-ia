# Modelo de Datos: Pantalla de Login

**Funcionalidad**: Pantalla de Login  
**Fecha**: 2026-03-07  
**Fase**: Phase 1 - Diseño de Datos

## Resumen

Este documento define las entidades de datos, sus atributos, relaciones, reglas de validación, y transiciones de estado para la funcionalidad de pantalla de login. El modelo está diseñado para soportar autenticación JWT con refresh automático, validación de formularios, y gestión de sesiones de usuario.

---

## Entidades

### 1. Usuario (User)

Representa un usuario autenticado en el sistema VoxIA.

#### Atributos

| Campo | Tipo | Requerido | Descripción | Validación |
|-------|------|-----------|-------------|------------|
| `id` | `string` | Sí | Identificador único del usuario (UUID) | UUID v4 válido |
| `username` | `string` | Sí | Nombre de usuario para login | 3-50 caracteres, alfanumérico + `._@-` |
| `displayName` | `string` | Sí | Nombre para mostrar en UI | 1-100 caracteres |
| `createdAt` | `Date` | Sí | Fecha de creación del usuario | ISO 8601 |
| `lastLoginAt` | `Date` | No | Última fecha de login exitoso | ISO 8601 |

#### Reglas de Negocio

- Los usuarios son **pre-creados por administradores** del sistema
- No existe flujo de auto-registro
- El `username` es **único** en el sistema
- El `username` es **case-insensitive** para login
- El `displayName` puede contener espacios y caracteres UTF-8

#### Ejemplo TypeScript

```typescript
interface User {
  id: string
  username: string
  displayName: string
  createdAt: Date
  lastLoginAt?: Date
}
```

---

### 2. Credenciales de Login (LoginCredentials)

Representa el par de credenciales enviado para autenticación.

#### Atributos

| Campo | Tipo | Requerido | Descripción | Validación |
|-------|------|-----------|-------------|------------|
| `username` | `string` | Sí | Nombre de usuario | 3-50 caracteres, regex: `/^[a-zA-Z0-9._@-]+$/` |
| `password` | `string` | Sí | Contraseña del usuario | 6-100 caracteres |

#### Reglas de Validación

**Username**:
- Mínimo: 3 caracteres
- Máximo: 50 caracteres
- Caracteres permitidos: `a-z`, `A-Z`, `0-9`, `.`, `_`, `@`, `-`
- Mensaje de error (< 3 chars): "Mínimo 3 caracteres"
- Mensaje de error (caracteres inválidos): "Usuario inválido"

**Password**:
- Mínimo: 6 caracteres
- Máximo: 100 caracteres
- Sin restricciones de caracteres (permite cualquier UTF-8)
- Mensaje de error (< 6 chars): "Mínimo 6 caracteres"

#### Validación en Cliente (Zod Schema)

```typescript
import { z } from 'zod'

export const loginSchema = z.object({
  username: z
    .string()
    .min(3, 'Mínimo 3 caracteres')
    .max(50, 'Máximo 50 caracteres')
    .regex(/^[a-zA-Z0-9._@-]+$/, 'Usuario inválido'),
  password: z
    .string()
    .min(6, 'Mínimo 6 caracteres')
    .max(100, 'Máximo 100 caracteres')
})

export type LoginCredentials = z.infer<typeof loginSchema>
```

#### Validación en Servidor

El servidor **debe** validar nuevamente las credenciales (nunca confiar solo en validación de cliente):
- Formato de username y password
- Existencia del usuario
- Coincidencia de contraseña (hash bcrypt)
- Estado del usuario (activo/inactivo)

---

### 3. Sesión de Autenticación (AuthSession)

Representa una sesión activa de usuario con tokens JWT.

#### Atributos

| Campo | Tipo | Requerido | Descripción | Almacenamiento |
|-------|------|-----------|-------------|----------------|
| `accessToken` | `string` | Sí | JWT access token | Memoria (Zustand) |
| `refreshToken` | `string` | Sí | JWT refresh token | httpOnly Cookie |
| `user` | `User` | Sí | Datos del usuario autenticado | Memoria (Zustand) |
| `expiresAt` | `Date` | Sí | Fecha de expiración del access token | Calculado del JWT |

#### Ciclo de Vida

```
┌─────────────────────────────────────────────────────────────┐
│                    CICLO DE VIDA DE SESIÓN                  │
└─────────────────────────────────────────────────────────────┘

1. [INICIO] → Usuario ingresa credenciales

2. [VALIDACIÓN] → POST /api/auth/login
   ├─ Credenciales válidas → [AUTENTICADO]
   └─ Credenciales inválidas → [ERROR] → volver a [INICIO]

3. [AUTENTICADO] → Tokens almacenados
   ├─ accessToken → Zustand (memoria)
   └─ refreshToken → httpOnly cookie

4. [ACTIVO] → Usuario usa la aplicación
   ├─ Cada request incluye: Authorization: Bearer <accessToken>
   └─ Access token válido → [CONTINUAR]

5. [EXPIRACIÓN ACCESS TOKEN] → 401 Unauthorized
   ├─ Interceptor detecta 401
   ├─ POST /api/auth/refresh (automático)
   │  ├─ Refresh token válido → Nuevo accessToken → [ACTIVO]
   │  └─ Refresh token inválido/expirado → [LOGOUT]
   └─ [ACTIVO]

6. [LOGOUT] → Usuario cierra sesión o tokens expiran
   ├─ Limpiar accessToken de Zustand
   ├─ Limpiar user de Zustand
   ├─ Backend invalida refresh token
   └─ Redirect a / (login)
```

#### Transiciones de Estado

| Estado Actual | Evento | Estado Siguiente | Acción |
|---------------|--------|------------------|--------|
| No Autenticado | Login exitoso | Autenticado | Almacenar tokens, redirect a /dashboard |
| No Autenticado | Login fallido | No Autenticado | Mostrar error, limpiar password |
| Autenticado | Access token expira | Refrescando | Llamar /api/auth/refresh |
| Refrescando | Refresh exitoso | Autenticado | Actualizar accessToken, reintentar request |
| Refrescando | Refresh fallido | No Autenticado | Logout, redirect a / |
| Autenticado | Logout manual | No Autenticado | Limpiar tokens, redirect a / |
| Autenticado | Inactividad (7 días) | No Autenticado | Refresh token expira, logout automático |

#### Ejemplo TypeScript

```typescript
interface AuthSession {
  accessToken: string
  user: User
  expiresAt: Date
}

interface AuthState {
  session: AuthSession | null
  isAuthenticated: boolean
  isLoading: boolean
}
```

---

### 4. Estado del Formulario (FormState)

Representa el estado del formulario de login en la UI.

#### Atributos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `username` | `string` | Sí | Valor actual del campo username |
| `password` | `string` | Sí | Valor actual del campo password |
| `errors` | `FormErrors` | No | Errores de validación por campo |
| `isSubmitting` | `boolean` | Sí | Indica si el formulario se está enviando |
| `showPassword` | `boolean` | Sí | Indica si la contraseña es visible |
| `attemptCount` | `number` | Sí | Número de intentos fallidos |
| `isRateLimited` | `boolean` | Sí | Indica si está bloqueado por rate limiting |
| `rateLimitCountdown` | `number` | No | Segundos restantes de bloqueo |

#### Reglas de Estado

**Validación**:
- Validación se ejecuta en evento `blur` de cada campo
- Validación NO se ejecuta mientras el usuario escribe (`onChange`)
- Errores se muestran inline debajo del campo correspondiente

**Botón de Envío**:
- Deshabilitado si: `username === ''` OR `password === ''` OR `errors.username` OR `errors.password` OR `isSubmitting` OR `isRateLimited`
- Habilitado si: todos los campos válidos y no está enviando

**Rate Limiting**:
- Se activa después de N intentos fallidos (definido por backend)
- Muestra countdown en el botón
- Deshabilita formulario durante el countdown
- Se resetea cuando countdown llega a 0

#### Ejemplo TypeScript

```typescript
interface FormErrors {
  username?: string
  password?: string
}

interface FormState {
  username: string
  password: string
  errors: FormErrors
  isSubmitting: boolean
  showPassword: boolean
  attemptCount: number
  isRateLimited: boolean
  rateLimitCountdown?: number
}
```

---

## Relaciones entre Entidades

```
┌──────────────────────┐
│  LoginCredentials    │
│  - username          │
│  - password          │
└──────────┬───────────┘
           │
           │ (valida contra)
           ▼
┌──────────────────────┐
│       User           │
│  - id                │
│  - username          │
│  - displayName       │
│  - createdAt         │
│  - lastLoginAt       │
└──────────┬───────────┘
           │
           │ (genera)
           ▼
┌──────────────────────┐
│    AuthSession       │
│  - accessToken       │
│  - user ────────────┐│
│  - expiresAt        ││
└─────────────────────┘│
                       │
           ┌───────────┘
           │ (referencia)
           ▼
┌──────────────────────┐
│       User           │
│  (datos en sesión)   │
└──────────────────────┘
```

**Relaciones**:
1. `LoginCredentials` → `User`: Credenciales se validan contra usuario existente (1:1)
2. `User` → `AuthSession`: Usuario autenticado genera sesión (1:1)
3. `AuthSession` → `User`: Sesión contiene referencia a datos de usuario (1:1)
4. `FormState`: Estado local de UI, no persiste (efímero)

---

## Reglas de Validación Consolidadas

### Validación de Username

```typescript
const usernameRules = {
  minLength: 3,
  maxLength: 50,
  pattern: /^[a-zA-Z0-9._@-]+$/,
  messages: {
    tooShort: 'Mínimo 3 caracteres',
    tooLong: 'Máximo 50 caracteres',
    invalidChars: 'Usuario inválido'
  }
}
```

### Validación de Password

```typescript
const passwordRules = {
  minLength: 6,
  maxLength: 100,
  messages: {
    tooShort: 'Mínimo 6 caracteres',
    tooLong: 'Máximo 100 caracteres'
  }
}
```

### Validación de Sesión

```typescript
const sessionRules = {
  accessTokenDuration: 15 * 60, // 15 minutos en segundos
  refreshTokenDuration: 7 * 24 * 60 * 60, // 7 días en segundos
  maxLoginAttempts: 5, // Definido por backend
  rateLimitDuration: 5 * 60 // 5 minutos en segundos
}
```

---

## Persistencia y Almacenamiento

| Entidad | Almacenamiento | Duración | Notas |
|---------|----------------|----------|-------|
| `User` | Backend DB + Zustand | Permanente (DB), Sesión (Zustand) | Solo datos básicos en Zustand |
| `LoginCredentials` | Ninguno | Efímero | Nunca almacenar, solo transmitir |
| `AuthSession.accessToken` | Zustand (memoria) | 15 minutos | Se pierde al cerrar tab/refresh |
| `AuthSession.refreshToken` | httpOnly Cookie | 7 días | Gestionado por backend |
| `FormState` | React Hook Form | Efímero | Se pierde al desmontar componente |

**Seguridad**:
- ❌ NUNCA almacenar `accessToken` en `localStorage` (vulnerable a XSS)
- ❌ NUNCA almacenar `password` en ningún lado
- ✅ `refreshToken` SOLO en httpOnly cookie (no accesible desde JS)
- ✅ `accessToken` SOLO en memoria (Zustand sin persistencia)

---

## Diagrama de Flujo de Datos

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO DE DATOS - LOGIN                   │
└─────────────────────────────────────────────────────────────┘

1. Usuario ingresa credenciales
   ↓
2. FormState actualiza (onChange)
   ↓
3. Usuario deja campo (onBlur)
   ↓
4. Validación Zod ejecuta
   ├─ Válido → Limpiar error
   └─ Inválido → Mostrar error
   ↓
5. Usuario hace submit
   ↓
6. Validación completa del formulario
   ├─ Inválido → Mostrar errores, detener
   └─ Válido → Continuar
   ↓
7. isSubmitting = true (deshabilitar botón)
   ↓
8. POST /api/auth/login con LoginCredentials
   ↓
9. Backend responde
   ├─ 200 OK → { accessToken, refreshToken, user }
   │   ├─ Almacenar accessToken en Zustand
   │   ├─ Almacenar user en Zustand
   │   ├─ refreshToken automático en cookie (backend)
   │   └─ Redirect a /dashboard
   │
   ├─ 401 Unauthorized → Credenciales inválidas
   │   ├─ toast.error('Usuario o contraseña incorrectos')
   │   ├─ Limpiar campo password
   │   ├─ Focus en password
   │   └─ attemptCount++
   │
   ├─ 429 Too Many Requests → Rate limiting
   │   ├─ toast.warning('Demasiados intentos...')
   │   ├─ isRateLimited = true
   │   ├─ Iniciar countdown
   │   └─ Deshabilitar formulario
   │
   └─ 500/Network Error → Error de servidor
       ├─ toast.error('No pudimos conectar con el servidor')
       └─ isSubmitting = false
   ↓
10. isSubmitting = false (habilitar botón si no hay rate limit)
```

---

## Próximos Pasos

1. ✅ Modelo de datos definido
2. → Generar `contracts/api-contracts.md` (contratos de API backend)
3. → Generar `quickstart.md` (guía de desarrollo)
4. → Generar `tasks.md` (Phase 2 - comando separado)
