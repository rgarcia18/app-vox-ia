# Investigación: Pantalla de Login

**Funcionalidad**: Pantalla de Login  
**Fecha**: 2026-03-07  
**Fase**: Phase 0 - Investigación y Decisiones Técnicas

## Resumen Ejecutivo

Esta investigación resuelve las decisiones técnicas clave para implementar la pantalla de login de VoxIA, incluyendo estrategia de autenticación JWT, validación de formularios, gestión de estado, y mejores prácticas de seguridad. Todas las decisiones están alineadas con los requerimientos de la especificación y la constitución del proyecto.

---

## 1. Estrategia de Autenticación JWT

### Decisión
Implementar autenticación basada en JWT con patrón de **access token + refresh token**:
- **Access token**: Almacenado en memoria (Zustand store), duración corta (15 minutos)
- **Refresh token**: Almacenado en httpOnly cookie, duración larga (7 días)
- **Interceptor Axios**: Refresh automático del access token cuando expira (401)

### Fundamento
- **Seguridad XSS**: Nunca almacenar access token en localStorage previene robo de tokens vía XSS
- **Usabilidad**: Refresh automático evita que el usuario tenga que re-autenticarse cada 15 minutos
- **Seguridad CSRF**: httpOnly cookie no es accesible desde JavaScript, mitigando ataques CSRF
- **Estándar de industria**: Patrón ampliamente adoptado y probado en producción

### Alternativas Consideradas
1. **Session-based auth con cookies**: Rechazado - requiere estado en servidor, no escala bien para SPA
2. **Access token en localStorage**: Rechazado - vulnerable a XSS (violación de constitución de seguridad)
3. **Solo access token sin refresh**: Rechazado - mala UX (usuario debe re-autenticarse frecuentemente)

### Implementación
```typescript
// stores/authStore.ts
interface AuthState {
  accessToken: string | null
  user: User | null
  setAccessToken: (token: string) => void
  setUser: (user: User) => void
  logout: () => void
}

// services/api.ts - Interceptor de refresh automático
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const { data } = await api.post('/api/auth/refresh')
        useAuthStore.getState().setAccessToken(data.access_token)
        original.headers['Authorization'] = `Bearer ${data.access_token}`
        return api(original)
      } catch {
        useAuthStore.getState().logout()
        window.location.href = '/'
      }
    }
    return Promise.reject(error)
  }
)
```

---

## 2. Validación de Formularios

### Decisión
Utilizar **React Hook Form + Zod** para validación de formularios con las siguientes reglas:
- Validación en eventos **blur** (no durante escritura activa)
- Esquemas Zod tipados para username y password
- Mensajes de error en español alineados con UX

### Fundamento
- **Type Safety**: Zod proporciona validación tipada que se integra perfectamente con TypeScript
- **Performance**: React Hook Form minimiza re-renders innecesarios
- **UX**: Validación en blur (no onChange) evita frustración del usuario mientras escribe
- **Mantenibilidad**: Esquemas Zod centralizados y reutilizables

### Alternativas Consideradas
1. **Formik + Yup**: Rechazado - React Hook Form tiene mejor performance y menor bundle size
2. **Validación manual con useState**: Rechazado - código repetitivo, propenso a errores
3. **Validación solo en submit**: Rechazado - mala UX, no cumple con requerimiento de feedback inmediato

### Implementación
```typescript
// lib/validations.ts
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

export type LoginFormData = z.infer<typeof loginSchema>
```

---

## 3. Gestión de Estado Global

### Decisión
Utilizar **Zustand** para gestión de estado de autenticación con las siguientes características:
- Store único `authStore` para access token y datos de usuario
- Persistencia NO habilitada (token solo en memoria)
- Acciones: `setAccessToken`, `setUser`, `logout`

### Fundamento
- **Simplicidad**: API minimalista sin boilerplate (vs Redux)
- **Performance**: Re-renders optimizados automáticamente
- **TypeScript**: Soporte first-class para tipos
- **Bundle Size**: ~1KB vs ~8KB de Redux
- **Seguridad**: No persistencia por defecto previene almacenamiento accidental en localStorage

### Alternativas Consideradas
1. **Redux Toolkit**: Rechazado - demasiado boilerplate para caso de uso simple
2. **Context API + useReducer**: Rechazado - performance inferior, más código
3. **Jotai/Recoil**: Rechazado - atomic state no necesario para este caso de uso

### Implementación
```typescript
// stores/authStore.ts
import { create } from 'zustand'

interface User {
  id: string
  username: string
  displayName: string
}

interface AuthState {
  accessToken: string | null
  user: User | null
  setAccessToken: (token: string) => void
  setUser: (user: User) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  setAccessToken: (token) => set({ accessToken: token }),
  setUser: (user) => set({ user }),
  logout: () => set({ accessToken: null, user: null })
}))
```

---

## 4. Protección de Rutas

### Decisión
Implementar **Next.js Middleware** para protección de rutas con las siguientes reglas:
- Rutas públicas: `/` (login)
- Rutas protegidas: `/dashboard/*` (requieren autenticación)
- Redirección automática: usuarios autenticados en `/` → `/dashboard`
- Redirección automática: usuarios no autenticados en rutas protegidas → `/`

### Fundamento
- **Server-Side**: Middleware ejecuta en edge, previene acceso antes de renderizar
- **Performance**: Redirecciones rápidas sin cargar componentes innecesarios
- **Seguridad**: Validación de tokens en servidor, no solo cliente
- **Next.js Native**: Patrón recomendado por Next.js 14+

### Alternativas Consideradas
1. **Client-side guards con useEffect**: Rechazado - flash de contenido no autorizado, menos seguro
2. **getServerSideProps en cada página**: Rechazado - código repetitivo, menos performante
3. **Higher-Order Components**: Rechazado - patrón obsoleto en App Router

### Implementación
```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('refresh_token')
  const isLoginPage = request.nextUrl.pathname === '/'
  const isProtectedRoute = request.nextUrl.pathname.startsWith('/dashboard')

  // Usuario autenticado en login → redirigir a dashboard
  if (token && isLoginPage) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  // Usuario no autenticado en ruta protegida → redirigir a login
  if (!token && isProtectedRoute) {
    return NextResponse.redirect(new URL('/', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/', '/dashboard/:path*']
}
```

---

## 5. Manejo de Errores y Notificaciones

### Decisión
Utilizar **Sonner** para notificaciones toast con las siguientes características:
- Errores de autenticación: toast.error con mensaje genérico
- Errores de red: toast.error con mensaje específico
- Rate limiting: toast.warning con countdown
- Posición: bottom-right
- Duración: 4000ms (ajustable por tipo)

### Fundamento
- **UX**: Feedback visual claro sin bloquear interfaz
- **Accesibilidad**: Sonner incluye ARIA labels automáticamente
- **Customización**: Fácil personalización de estilos con Tailwind
- **Bundle Size**: ~3KB, más ligero que react-hot-toast

### Alternativas Consideradas
1. **react-hot-toast**: Rechazado - bundle size mayor, menos customizable
2. **Mensajes inline en formulario**: Rechazado - no cubre errores de red/servidor
3. **Modal de error**: Rechazado - interrumpe flujo del usuario

### Implementación
```typescript
// components/shared/LoginForm.tsx
import { toast } from 'sonner'

const onSubmit = async (data: LoginFormData) => {
  try {
    const response = await api.post('/api/auth/login', data)
    // ...
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 401) {
        toast.error('Usuario o contraseña incorrectos')
      } else if (error.response?.status === 429) {
        toast.warning('Demasiados intentos. Espera unos minutos')
      } else {
        toast.error('No pudimos conectar con el servidor')
      }
    }
  }
}
```

---

## 6. Animaciones y Transiciones

### Decisión
Utilizar **Framer Motion** para animaciones con las siguientes características:
- Entrada de card: fade + slide up (duration: 0.5s, ease: easeOut)
- Hover en botón: scale 1.02 + shadow increase
- Salida post-login: fade out (duration: 0.3s)
- Fondo animado: gradient shift sutil

### Fundamento
- **Performance**: Animaciones GPU-accelerated
- **Declarativo**: API React-friendly
- **Accesibilidad**: Respeta prefers-reduced-motion automáticamente
- **Requerimiento**: Especificación requiere animaciones suaves

### Alternativas Consideradas
1. **CSS Transitions**: Rechazado - menos control, no respeta prefers-reduced-motion fácilmente
2. **GSAP**: Rechazado - bundle size mayor, overkill para caso de uso
3. **React Spring**: Rechazado - API más compleja, menos documentación

### Implementación
```typescript
// components/shared/LoginForm.tsx
import { motion } from 'framer-motion'

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0 }}
  transition={{ duration: 0.5, ease: 'easeOut' }}
>
  {/* Formulario */}
</motion.div>
```

---

## 7. Testing Strategy

### Decisión
Implementar testing en tres niveles:
1. **Unit Tests** (Jest + React Testing Library):
   - Componentes: LoginForm, Logo
   - Stores: authStore
   - Validaciones: loginSchema
   - Coverage objetivo: 80%+

2. **Integration Tests** (Playwright):
   - Flujo completo de login exitoso
   - Manejo de credenciales inválidas
   - Rate limiting
   - Redirecciones automáticas

3. **Accessibility Tests** (jest-axe):
   - Validación WCAG 2.1 AA
   - Contraste de colores
   - Navegación por teclado

### Fundamento
- **Calidad**: Tests previenen regresiones
- **Constitución**: Requerimiento de tests para lógica crítica
- **Confianza**: Coverage alto permite refactoring seguro
- **CI/CD**: Tests automáticos en pipeline

### Alternativas Consideradas
1. **Solo E2E tests**: Rechazado - lentos, difíciles de debuggear
2. **Solo unit tests**: Rechazado - no validan integración real
3. **Cypress**: Rechazado - Playwright tiene mejor performance y API

---

## Resumen de Decisiones Técnicas

| Área | Tecnología | Justificación |
|------|-----------|---------------|
| Autenticación | JWT (access + refresh) | Seguridad XSS, UX, estándar industria |
| Validación | React Hook Form + Zod | Type safety, performance, UX |
| Estado Global | Zustand | Simplicidad, performance, bundle size |
| Protección Rutas | Next.js Middleware | Server-side, seguridad, performance |
| Notificaciones | Sonner | UX, accesibilidad, bundle size |
| Animaciones | Framer Motion | Performance, accesibilidad, requerimiento |
| Testing | Jest + RTL + Playwright | Calidad, coverage, confianza |

---

## Próximos Pasos

1. ✅ Research completado
2. → Generar `data-model.md` (Phase 1)
3. → Generar `contracts/api-contracts.md` (Phase 1)
4. → Generar `quickstart.md` (Phase 1)
5. → Generar `tasks.md` (Phase 2 - comando separado)
