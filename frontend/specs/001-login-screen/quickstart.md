# Guía de Inicio Rápido: Pantalla de Login

**Funcionalidad**: Pantalla de Login  
**Fecha**: 2026-03-07  
**Fase**: Phase 1 - Guía de Desarrollo

## Resumen

Esta guía proporciona instrucciones paso a paso para configurar el entorno de desarrollo e implementar la pantalla de login de VoxIA. Incluye instalación de dependencias, configuración del proyecto, y verificación de que todo funciona correctamente.

---

## Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

- **Node.js**: v18.17.0 o superior
- **npm**: v9.0.0 o superior (o yarn/pnpm)
- **Git**: Para control de versiones
- **Editor de código**: VS Code recomendado con extensiones:
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense
  - TypeScript and JavaScript Language Features

---

## Paso 1: Configuración Inicial del Proyecto

### 1.1 Verificar Proyecto Next.js

El proyecto ya debe estar inicializado con Next.js 14+. Verifica la versión:

```bash
cd app-voxia-frontend
cat package.json | grep "next"
```

Deberías ver: `"next": "16.1.6"` o superior.

### 1.2 Instalar Dependencias Base

Si aún no están instaladas, ejecuta:

```bash
npm install
```

---

## Paso 2: Instalar Dependencias de la Funcionalidad

### 2.1 Dependencias de UI y Estilos

```bash
# shadcn/ui (componentes base)
# Usar --defaults para configuración automática con Next.js
npx shadcn@latest init --defaults

# O configuración manual (sin --defaults):
npx shadcn@latest init
# Cuando pregunte:
# - Would you like to use TypeScript? → Yes
# - Which style would you like to use? → Default
# - Which color would you like to use as base color? → Slate
# - Where is your global CSS file? → app/globals.css
# - Would you like to use CSS variables for colors? → Yes
# - Where is your tailwind.config.js located? → tailwind.config.ts
# - Configure the import alias for components → @/components
# - Configure the import alias for utils → @/lib/utils

# Instalar componentes específicos de shadcn/ui
npx shadcn@latest add button input form label

# Iconos
npm install lucide-react

# Animaciones
npm install framer-motion
```

### 2.2 Dependencias de Formularios y Validación

```bash
npm install react-hook-form zod @hookform/resolvers
```

### 2.3 Dependencias de Estado y HTTP

```bash
# Gestión de estado
npm install zustand

# Cliente HTTP
npm install axios

# Notificaciones
npm install sonner
```

### 2.4 Dependencias de Desarrollo

```bash
npm install -D @types/node @types/react @types/react-dom
npm install -D jest @testing-library/react @testing-library/jest-dom
npm install -D @playwright/test
npm install -D jest-axe
```

---

## Paso 3: Configuración de Variables de Entorno

### 3.1 Crear Archivo .env.local

```bash
touch .env.local
```

### 3.2 Agregar Variables de Entorno

Edita `.env.local` y agrega:

```bash
# URL del backend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Entorno
NODE_ENV=development
```

**Nota**: Nunca commitear `.env.local` al repositorio. Ya debe estar en `.gitignore`.

---

## Paso 4: Configuración de TypeScript

### 4.1 Verificar tsconfig.json

Asegúrate de que `tsconfig.json` tenga configuración estricta:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

---

## Paso 5: Estructura de Archivos

### 5.1 Crear Directorios

```bash
# Desde la raíz del proyecto
mkdir -p components/shared
mkdir -p components/ui
mkdir -p stores
mkdir -p services
mkdir -p lib
mkdir -p __tests__/unit
mkdir -p __tests__/integration
```

### 5.2 Verificar Estructura

```bash
tree -L 2 -I 'node_modules'
```

Deberías ver:

```
app-voxia-frontend/
├── app/
│   ├── page.tsx
│   ├── layout.tsx
│   └── globals.css
├── components/
│   ├── shared/
│   └── ui/
├── stores/
├── services/
├── lib/
├── __tests__/
│   ├── unit/
│   └── integration/
├── public/
├── specs/
│   └── 001-login-screen/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

---

## Paso 6: Implementación Paso a Paso

### 6.1 Crear Zustand Auth Store

**Archivo**: `stores/authStore.ts`

```typescript
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

### 6.2 Crear Cliente Axios

**Archivo**: `services/api.ts`

```typescript
import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
})

// Request interceptor: agregar access token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: refresh automático
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config

    if (
      error.response?.status === 401 &&
      !original._retry &&
      !original.url?.includes('/auth/refresh')
    ) {
      original._retry = true

      try {
        const { data } = await api.post('/api/auth/refresh')
        useAuthStore.getState().setAccessToken(data.access_token)
        original.headers.Authorization = `Bearer ${data.access_token}`
        return api(original)
      } catch {
        useAuthStore.getState().logout()
        window.location.href = '/'
      }
    }

    return Promise.reject(error)
  }
)

export default api
```

### 6.3 Crear Esquemas de Validación

**Archivo**: `lib/validations.ts`

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

export type LoginFormData = z.infer<typeof loginSchema>
```

### 6.4 Crear Componente Logo

**Archivo**: `components/shared/Logo.tsx`

```typescript
import { Mic } from 'lucide-react'

export function Logo() {
  return (
    <div className="flex items-center gap-2">
      <div className="rounded-full bg-blue-600 p-2">
        <Mic className="h-6 w-6 text-white" />
      </div>
      <div>
        <h1 className="text-2xl font-bold text-gray-900">VoxIA</h1>
        <p className="text-sm text-gray-600">Transcripción inteligente de reuniones</p>
      </div>
    </div>
  )
}
```

### 6.5 Crear Formulario de Login

**Archivo**: `components/shared/LoginForm.tsx`

Ver implementación completa en `specs/001-login-screen/tasks.md` (se generará con `/speckit.tasks`).

### 6.6 Actualizar Página Principal

**Archivo**: `app/page.tsx`

```typescript
import { LoginForm } from '@/components/shared/LoginForm'
import { Logo } from '@/components/shared/Logo'

export default function LoginPage() {
  return (
    <main className="min-h-screen bg-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <Logo />
        </div>
        <LoginForm />
      </div>
    </main>
  )
}
```

### 6.7 Crear Middleware de Protección

**Archivo**: `middleware.ts`

```typescript
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('refresh_token')
  const isLoginPage = request.nextUrl.pathname === '/'
  const isProtectedRoute = request.nextUrl.pathname.startsWith('/dashboard')

  if (token && isLoginPage) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

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

## Paso 7: Configuración de Testing

### 7.1 Configurar Jest

**Archivo**: `jest.config.js`

```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './'
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1'
  }
}

module.exports = createJestConfig(customJestConfig)
```

**Archivo**: `jest.setup.js`

```javascript
import '@testing-library/jest-dom'
```

### 7.2 Configurar Playwright

```bash
npx playwright install
```

**Archivo**: `playwright.config.ts`

```typescript
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './__tests__/integration',
  use: {
    baseURL: 'http://localhost:3000'
  },
  webServer: {
    command: 'npm run dev',
    port: 3000
  }
})
```

---

## Paso 8: Ejecutar y Verificar

### 8.1 Iniciar Servidor de Desarrollo

```bash
npm run dev
```

Abre http://localhost:3000 en tu navegador.

### 8.2 Verificar Funcionalidad Básica

- [ ] La página de login se carga correctamente
- [ ] El logo de VoxIA se muestra
- [ ] Los campos de username y password están presentes
- [ ] El botón de submit está deshabilitado cuando los campos están vacíos
- [ ] La validación funciona en eventos blur

### 8.3 Ejecutar Tests

```bash
# Unit tests
npm run test

# Integration tests
npm run test:e2e

# Coverage
npm run test:coverage
```

---

## Paso 9: Integración con Backend

### 9.1 Verificar Backend Corriendo

Asegúrate de que el backend esté corriendo en `http://localhost:8000`:

```bash
curl http://localhost:8000/api/health
```

### 9.2 Probar Login Real

1. Obtén credenciales de prueba del administrador
2. Ingresa en el formulario de login
3. Verifica que:
   - El login sea exitoso
   - Seas redirigido a `/dashboard`
   - El access token esté en Zustand
   - El refresh token esté en cookies

---

## Paso 10: Debugging y Troubleshooting

### 10.1 Problemas Comunes

**Error: "Module not found"**
```bash
# Limpiar caché y reinstalar
rm -rf node_modules package-lock.json
npm install
```

**Error: "CORS policy"**
```bash
# Verificar que backend tenga CORS configurado para http://localhost:3000
```

**Error: "Cookies not being set"**
```bash
# Verificar que withCredentials: true esté en axios
# Verificar que backend setee cookies con SameSite=None en desarrollo
```

### 10.2 Herramientas de Debugging

**React DevTools**:
- Instalar extensión de navegador
- Inspeccionar estado de Zustand

**Network Tab**:
- Verificar requests a `/api/auth/login`
- Verificar headers (Authorization, Cookie)
- Verificar responses

**Console**:
```typescript
// Agregar logs temporales
console.log('Access Token:', useAuthStore.getState().accessToken)
console.log('User:', useAuthStore.getState().user)
```

---

## Paso 11: Checklist de Completitud

Antes de considerar la funcionalidad completa, verifica:

### Funcionalidad
- [ ] Login con credenciales válidas funciona
- [ ] Login con credenciales inválidas muestra error
- [ ] Validación de formulario funciona (blur)
- [ ] Botón de submit se deshabilita apropiadamente
- [ ] Alternancia de visibilidad de password funciona
- [ ] Redirección a dashboard funciona
- [ ] Middleware protege rutas correctamente
- [ ] Refresh automático de token funciona
- [ ] Logout funciona

### Calidad de Código
- [ ] TypeScript sin errores (`npm run type-check`)
- [ ] ESLint sin errores (`npm run lint`)
- [ ] Prettier formateado (`npm run format`)
- [ ] Tests unitarios pasan (`npm run test`)
- [ ] Tests E2E pasan (`npm run test:e2e`)
- [ ] Coverage > 80% en lógica crítica

### Accesibilidad
- [ ] Navegación por teclado funciona (Tab, Enter)
- [ ] Lectores de pantalla funcionan (ARIA labels)
- [ ] Contraste de colores cumple WCAG AA
- [ ] Focus visible en todos los elementos interactivos

### Performance
- [ ] Carga inicial < 1 segundo
- [ ] Validación < 200ms
- [ ] Login completo < 10 segundos

### Seguridad
- [ ] Access token NUNCA en localStorage
- [ ] Refresh token en httpOnly cookie
- [ ] Mensajes de error genéricos (no revelan info)
- [ ] Rate limiting funciona

---

## Próximos Pasos

1. ✅ Quickstart completado
2. → Ejecutar `/speckit.tasks` para generar lista detallada de tareas
3. → Implementar tareas en orden de prioridad
4. → Ejecutar tests continuamente
5. → Hacer commits frecuentes con mensajes en español

---

## Recursos Adicionales

### Documentación
- [Next.js 14 Docs](https://nextjs.org/docs)
- [React Hook Form](https://react-hook-form.com/)
- [Zod](https://zod.dev/)
- [Zustand](https://docs.pmnd.rs/zustand)
- [shadcn/ui](https://ui.shadcn.com/)
- [Framer Motion](https://www.framer.com/motion/)

### Especificaciones del Proyecto
- `specs/001-login-screen/spec.md` - Especificación funcional
- `specs/001-login-screen/plan.md` - Plan de implementación
- `specs/001-login-screen/research.md` - Decisiones técnicas
- `specs/001-login-screen/data-model.md` - Modelo de datos
- `specs/001-login-screen/contracts/api-contracts.md` - Contratos de API

### Constitución del Proyecto
- `.specify/memory/constitution.md` - Principios y estándares del proyecto
