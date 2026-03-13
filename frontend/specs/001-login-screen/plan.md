# Plan de Implementación: Pantalla de Login

**Rama**: `001-login-screen` | **Fecha**: 2026-03-07 | **Spec**: [spec.md](./spec.md)
**Entrada**: Especificación de funcionalidad desde `/specs/001-login-screen/spec.md`

## Resumen

Implementar la pantalla de login como punto de entrada al sistema VoxIA. La funcionalidad central incluye autenticación de usuarios mediante JWT (access token + refresh token), validación de formularios en tiempo real, manejo de errores de seguridad, y protección contra ataques de fuerza bruta mediante rate limiting. El enfoque técnico utiliza Next.js 14+ con App Router, React Hook Form + Zod para validación, Zustand para gestión de estado de autenticación, y Axios con interceptores para manejo automático de refresh de tokens.

## Contexto Técnico

**Lenguaje/Versión**: TypeScript 5+ con modo estricto habilitado  
**Dependencias Principales**: Next.js 14+, React 18+, Tailwind CSS 3.4+, shadcn/ui, React Hook Form, Zod, Zustand, Axios, Framer Motion 11+, Lucide React, Sonner  
**Almacenamiento**: Access token en memoria (Zustand), Refresh token en httpOnly cookie (gestionado por backend)  
**Testing**: Jest + React Testing Library para unit tests, Playwright para tests de integración  
**Plataforma Objetivo**: Navegadores web modernos (Chrome, Firefox, Safari, Edge - últimas 2 versiones)  
**Tipo de Proyecto**: Aplicación web (frontend Next.js)  
**Objetivos de Rendimiento**: 
- Carga inicial < 1 segundo en banda ancha estándar
- Validación de formulario < 200ms en eventos blur
- Redirección post-login < 500ms
- Login completo < 10 segundos (credenciales válidas + red normal)

**Restricciones**: 
- Access token NUNCA en localStorage (seguridad XSS)
- Validación solo en blur, no durante escritura activa
- Cumplimiento WCAG 2.1 AA
- Ratio de contraste mínimo 4.5:1

**Escala/Alcance**: Pantalla única de login, ~5-8 componentes React, ~500-800 líneas de código

## Constitution Check

*GATE: Debe pasar antes de Phase 0 research. Re-verificar después de Phase 1 design.*

### ✅ Principio I: Spanish-First Specifications
- Especificación en español: ✅ CUMPLE
- Comentarios de código: Deben estar en español
- Mensajes de commit: Deben estar en español
- Documentación técnica: Debe estar en español

### ✅ Principio II: Clean Code & Design Patterns
- TypeScript strict mode: ✅ REQUERIDO
- Componentes con responsabilidad única: ✅ REQUERIDO
- Patrones: Observer (Zustand), Strategy (validación), Factory (componentes shadcn/ui)
- DRY: Extraer lógica reutilizable (validación, API calls, manejo de errores)
- Sin tipos `any` sin justificación explícita

### ✅ Principio III: Strategic Documentation
Documentación REQUERIDA para:
- Interceptor Axios (lógica compleja de refresh automático)
- Zustand authStore (gestión de estado de autenticación)
- Middleware de protección de rutas
- Funciones de validación custom con Zod

Documentación NO requerida para:
- Componentes shadcn/ui estándar
- Getters/setters simples
- Operaciones CRUD obvias

**Estado del Gate**: ✅ APROBADO - No hay violaciones de constitución

## Estructura del Proyecto

### Documentación (esta funcionalidad)

```text
specs/001-login-screen/
├── plan.md              # Este archivo (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── api-contracts.md # Contratos de API backend
└── tasks.md             # Phase 2 output (/speckit.tasks command - NO creado por /speckit.plan)
```

### Código Fuente (raíz del repositorio)

```text
app-voxia-frontend/
├── app/
│   ├── page.tsx                              # Página de login (ruta /)
│   ├── layout.tsx                            # Layout global con fuentes y providers
│   ├── dashboard/
│   │   └── page.tsx                          # Dashboard (ruta protegida)
│   └── globals.css                           # Estilos globales Tailwind
│
├── components/
│   ├── shared/
│   │   ├── Logo.tsx                          # Logo VoxIA reutilizable
│   │   ├── AnimatedBackground.tsx            # Fondo animado con Framer Motion
│   │   └── LoginForm.tsx                     # Formulario de login
│   └── ui/                                   # Componentes shadcn/ui
│       ├── button.tsx
│       ├── input.tsx
│       ├── form.tsx
│       └── label.tsx
│
├── stores/
│   └── authStore.ts                          # Zustand store de autenticación
│
├── services/
│   └── api.ts                                # Cliente Axios con interceptores JWT
│
├── lib/
│   ├── utils.ts                              # Utilidades (cn helper, etc.)
│   └── validations.ts                        # Esquemas Zod de validación
│
├── middleware.ts                             # Protección de rutas Next.js
│
├── __tests__/
│   ├── unit/
│   │   ├── LoginForm.test.tsx
│   │   ├── authStore.test.ts
│   │   └── validations.test.ts
│   └── integration/
│       └── login-flow.spec.ts                # Playwright test
│
├── public/
│   └── logo.svg                              # Logo VoxIA
│
├── tailwind.config.ts                        # Configuración Tailwind
├── next.config.js                            # Configuración Next.js
├── tsconfig.json                             # Configuración TypeScript
└── package.json                              # Dependencias del proyecto
```

**Decisión de Estructura**: Aplicación web Next.js con App Router. Se utiliza la estructura estándar de Next.js 14+ con separación clara entre componentes de UI (`components/`), lógica de negocio (`stores/`, `services/`), y utilidades (`lib/`). Los tests se organizan por tipo (unit/integration) para facilitar ejecución selectiva.

## Seguimiento de Complejidad

> **Llenar SOLO si Constitution Check tiene violaciones que deben justificarse**

*No aplica - no hay violaciones de constitución.*
