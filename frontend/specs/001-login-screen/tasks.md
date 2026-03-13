# Tareas: Pantalla de Login

**Entrada**: Documentos de diseño desde `/specs/001-login-screen/`
**Prerrequisitos**: plan.md (requerido), spec.md (requerido), research.md, data-model.md, contracts/api-contracts.md

**Tests**: Los tests NO están incluidos en esta lista de tareas ya que no fueron explícitamente solicitados en la especificación. Se pueden agregar posteriormente si se requiere un enfoque TDD.

**Organización**: Las tareas están agrupadas por historia de usuario para permitir implementación y pruebas independientes de cada historia.

## Formato: `[ID] [P?] [Story] Descripción`

- **[P]**: Puede ejecutarse en paralelo (archivos diferentes, sin dependencias)
- **[Story]**: A qué historia de usuario pertenece esta tarea (ej: US1, US2, US3)
- Incluye rutas exactas de archivos en las descripciones

## Convenciones de Rutas

Basado en plan.md, este es un proyecto Next.js con la siguiente estructura:
- **App Router**: `app/` para páginas y layouts
- **Componentes**: `components/shared/` y `components/ui/`
- **Stores**: `stores/` para Zustand
- **Servicios**: `services/` para cliente API
- **Utilidades**: `lib/` para validaciones y helpers
- **Middleware**: `middleware.ts` en raíz

---

## Phase 1: Setup (Infraestructura Compartida)

**Propósito**: Inicialización del proyecto y estructura básica

- [x] T001 Verificar estructura del proyecto Next.js existente y crear directorios faltantes (components/shared, components/ui, stores, services, lib)
- [x] T002 [P] Instalar dependencias de UI: shadcn/ui (button, input, form, label), lucide-react, framer-motion
- [x] T003 [P] Instalar dependencias de formularios: react-hook-form, zod, @hookform/resolvers
- [x] T004 [P] Instalar dependencias de estado y HTTP: zustand, axios, sonner
- [x] T005 [P] Configurar variables de entorno en .env.local (NEXT_PUBLIC_API_URL)
- [x] T006 [P] Configurar TypeScript strict mode en tsconfig.json si no está habilitado
- [x] T007 [P] Configurar Tailwind CSS con fuentes Google (Sora para títulos, DM Sans para cuerpo)

---

## Phase 2: Foundational (Prerrequisitos Bloqueantes)

**Propósito**: Infraestructura central que DEBE completarse antes de que CUALQUIER historia de usuario pueda implementarse

**⚠️ CRÍTICO**: Ningún trabajo de historias de usuario puede comenzar hasta que esta fase esté completa

- [x] T008 Crear esquema de validación Zod para login en lib/validations.ts (username: 3-50 chars regex, password: 6-100 chars)
- [x] T009 Crear Zustand authStore en stores/authStore.ts (accessToken, user, setAccessToken, setUser, logout)
- [x] T010 Crear cliente Axios en services/api.ts con configuración base (baseURL, withCredentials, headers)
- [x] T011 Implementar request interceptor en services/api.ts para agregar Authorization header con accessToken
- [x] T012 Implementar response interceptor en services/api.ts para refresh automático de token en 401
- [x] T013 Crear middleware de protección de rutas en middleware.ts (redirigir autenticados de / a /dashboard, no autenticados de /dashboard a /)
- [x] T014 [P] Crear componente Logo en components/shared/Logo.tsx (ícono Mic, título VoxIA, tagline)
- [x] T015 [P] Crear utilidad cn helper en lib/utils.ts para merge de clases Tailwind (si no existe de shadcn/ui)

**Checkpoint**: Fundación lista - la implementación de historias de usuario puede comenzar en paralelo

---

## Phase 3: Historia de Usuario 1 - Autenticación Exitosa (Prioridad: P1) 🎯 MVP

**Objetivo**: Permitir que usuarios con credenciales válidas accedan al sistema VoxIA ingresando username y password, validando credenciales, y otorgando acceso al dashboard.

**Prueba Independiente**: Proporcionar credenciales válidas (username y password), enviar formulario, y verificar redirección exitosa al dashboard con estado de autenticación apropiado.

### Implementación para Historia de Usuario 1

- [x] T016 [P] [US1] Crear componente LoginForm en components/shared/LoginForm.tsx con estructura básica (form, campos username/password, botón submit)
- [x] T017 [P] [US1] Integrar React Hook Form en LoginForm con esquema Zod de validación
- [x] T018 [US1] Implementar lógica de submit en LoginForm: llamar POST /api/auth/login con axios
- [x] T019 [US1] Implementar manejo de respuesta exitosa en LoginForm: almacenar accessToken y user en Zustand, redirect a /dashboard
- [x] T020 [US1] Actualizar app/page.tsx para renderizar LoginForm con Logo y layout centrado (bg-blue-50)
- [x] T021 [US1] Crear página placeholder app/dashboard/page.tsx para verificar redirección
- [x] T022 [US1] Implementar soporte de submit con tecla Enter en cualquier campo del formulario
- [x] T023 [US1] Verificar que middleware redirija usuarios autenticados de / a /dashboard automáticamente

**Checkpoint**: En este punto, Historia de Usuario 1 debe ser completamente funcional y testeable independientemente

---

## Phase 4: Historia de Usuario 2 - Manejo de Credenciales Inválidas (Prioridad: P2)

**Objetivo**: Proporcionar retroalimentación clara cuando un usuario intenta login con credenciales incorrectas, sin revelar cuál credencial fue incorrecta (seguridad).

**Prueba Independiente**: Intentar login con varias combinaciones de credenciales inválidas y verificar que se muestren mensajes de error apropiados sin revelar detalles de seguridad.

### Implementación para Historia de Usuario 2

- [x] T024 [US2] Implementar manejo de error 401 en LoginForm: mostrar toast "Usuario o contraseña incorrectos" con Sonner
- [x] T025 [US2] Implementar limpieza de campo password después de error 401 en LoginForm
- [x] T026 [US2] Implementar retorno de foco automático al campo password después de error en LoginForm
- [x] T027 [US2] Asegurar que botón de login regrese a estado activo después de error para permitir reintento
- [x] T028 [US2] Implementar manejo de errores de red (500, 503) con toast "No pudimos conectar con el servidor"
- [x] T029 [US2] Agregar provider de Sonner (Toaster) en app/layout.tsx para notificaciones globales

**Checkpoint**: En este punto, Historias de Usuario 1 Y 2 deben funcionar independientemente

---

## Phase 5: Historia de Usuario 3 - Validación de Formulario y Guía al Usuario (Prioridad: P2)

**Objetivo**: Proporcionar retroalimentación de validación en tiempo real para asegurar que el usuario proporcione credenciales con formato apropiado antes del envío.

**Prueba Independiente**: Interactuar con campos del formulario (ingresar datos inválidos, dejar campos vacíos, etc.) y verificar que mensajes de validación apropiados aparezcan en los momentos correctos.

### Implementación para Historia de Usuario 3

- [x] T030 [US3] Configurar validación en eventos blur (no onChange) en LoginForm usando React Hook Form
- [x] T031 [US3] Implementar mensajes de error inline debajo de campos en LoginForm (username: "Mínimo 3 caracteres", "Usuario inválido")
- [x] T032 [US3] Implementar mensajes de error inline para password (password: "Mínimo 6 caracteres")
- [x] T033 [US3] Implementar lógica de deshabilitación de botón submit cuando campos vacíos o con errores de validación
- [x] T034 [US3] Implementar habilitación de botón submit con retroalimentación visual cuando validación pasa
- [x] T035 [US3] Agregar estilos de error a campos inválidos (borde rojo, texto de error en rojo)

**Checkpoint**: En este punto, Historias de Usuario 1, 2 Y 3 deben funcionar independientemente

---

## Phase 6: Historia de Usuario 4 - Alternancia de Visibilidad de Contraseña (Prioridad: P3)

**Objetivo**: Permitir que el usuario verifique que escribió su contraseña correctamente antes de enviar, alternando la visibilidad de la contraseña.

**Prueba Independiente**: Hacer clic en ícono de ojo en campo de contraseña y verificar que el texto de la contraseña alterna entre estados oculto y visible.

### Implementación para Historia de Usuario 4

- [x] T036 [P] [US4] Agregar estado showPassword en LoginForm para controlar visibilidad
- [x] T037 [US4] Agregar botón de toggle con íconos Eye/EyeOff de lucide-react en campo password
- [x] T038 [US4] Implementar lógica de toggle: cambiar type de input entre "password" y "text"
- [x] T039 [US4] Agregar etiquetas ARIA apropiadas al botón de toggle (aria-label: "Mostrar contraseña" / "Ocultar contraseña")
- [x] T040 [US4] Actualizar ícono dinámicamente según estado (Eye cuando oculto, EyeOff cuando visible)

**Checkpoint**: En este punto, Historias de Usuario 1, 2, 3 Y 4 deben funcionar independientemente

---

## Phase 7: Historia de Usuario 5 - Protección contra Limitación de Tasa (Prioridad: P3)

**Objetivo**: Bloquear temporalmente intentos adicionales de login cuando se detectan demasiados intentos fallidos, previniendo ataques de fuerza bruta.

**Prueba Independiente**: Realizar múltiples intentos fallidos de login en rápida sucesión y verificar que el sistema bloquee intentos adicionales con temporizador de cuenta regresiva.

### Implementación para Historia de Usuario 5

- [x] T041 [P] [US5] Agregar estados isRateLimited y rateLimitCountdown en LoginForm
- [x] T042 [US5] Implementar manejo de error 429 en LoginForm: extraer retry_after de respuesta
- [x] T043 [US5] Implementar toast de warning "Demasiados intentos. Espera unos minutos" en error 429
- [x] T044 [US5] Implementar countdown timer que actualiza cada segundo y muestra en botón de login
- [x] T045 [US5] Deshabilitar formulario completo durante período de rate limiting
- [x] T046 [US5] Habilitar formulario automáticamente cuando countdown llegue a 0
- [x] T047 [US5] Limpiar interval de countdown cuando componente se desmonte (cleanup)

**Checkpoint**: Todas las historias de usuario deben ser ahora independientemente funcionales

---

## Phase 8: Animaciones y Pulido Visual

**Propósito**: Agregar animaciones suaves y mejoras visuales que afectan múltiples historias de usuario

- [x] T048 [P] Crear componente AnimatedBackground en components/shared/AnimatedBackground.tsx con gradient shift sutil
- [x] T049 [P] Agregar animaciones de entrada a LoginForm con Framer Motion (fade + slide up, duration 0.5s)
- [x] T050 [P] Agregar animación de hover a botón de submit (scale 1.02, shadow increase)
- [x] T051 [P] Agregar animación de salida post-login con Framer Motion (fade out, duration 0.3s)
- [x] T052 [P] Implementar respeto a prefers-reduced-motion en todas las animaciones
- [x] T053 [P] Agregar estados de loading visual en botón durante submit (spinner, texto "Iniciando sesión...")
- [x] T054 [P] Agregar transiciones suaves a estados de focus en campos del formulario

---

## Phase 9: Accesibilidad y Cumplimiento WCAG

**Propósito**: Asegurar cumplimiento con WCAG 2.1 AA y accesibilidad completa

- [x] T055 [P] Verificar y ajustar ratios de contraste de colores (mínimo 4.5:1) en todos los elementos
- [x] T056 [P] Agregar etiquetas ARIA apropiadas a todos los campos del formulario
- [x] T057 [P] Verificar orden de tabulación correcto (username → password → toggle → submit)
- [x] T058 [P] Agregar estados de focus visibles a todos los elementos interactivos
- [x] T059 [P] Verificar que lectores de pantalla anuncien errores de validación correctamente
- [x] T060 [P] Agregar role="alert" a mensajes de error para anuncio inmediato

---

## Phase 10: Documentación y Configuración Final

**Propósito**: Completar documentación y configuración del proyecto

- [x] T061 [P] Agregar comentarios en español a funciones complejas (interceptor Axios, authStore, validaciones)
- [x] T062 [P] Crear archivo README.md en specs/001-login-screen/ con instrucciones de desarrollo
- [x] T063 [P] Verificar que todas las variables de entorno estén documentadas en .env.example
- [x] T064 [P] Ejecutar validación de quickstart.md para verificar que todas las instrucciones funcionen
- [x] T065 [P] Limpiar código: remover console.logs, comentarios innecesarios, imports no utilizados
- [x] T066 [P] Ejecutar linter (npm run lint) y corregir todos los warnings

---

## Dependencias y Orden de Ejecución

### Dependencias de Fases

- **Setup (Phase 1)**: Sin dependencias - puede comenzar inmediatamente
- **Foundational (Phase 2)**: Depende de Setup completo - BLOQUEA todas las historias de usuario
- **Historias de Usuario (Phase 3-7)**: Todas dependen de que Foundational phase esté completo
  - Las historias de usuario pueden proceder en paralelo (si hay personal)
  - O secuencialmente en orden de prioridad (P1 → P2 → P3)
- **Animaciones (Phase 8)**: Puede comenzar después de US1 completo, pero idealmente después de todas las US
- **Accesibilidad (Phase 9)**: Puede comenzar después de US1 completo, pero idealmente después de todas las US
- **Documentación (Phase 10)**: Depende de que todas las historias de usuario deseadas estén completas

### Dependencias de Historias de Usuario

- **Historia de Usuario 1 (P1)**: Puede comenzar después de Foundational (Phase 2) - Sin dependencias de otras historias
- **Historia de Usuario 2 (P2)**: Puede comenzar después de Foundational (Phase 2) - Extiende US1 pero es independientemente testeable
- **Historia de Usuario 3 (P2)**: Puede comenzar después de Foundational (Phase 2) - Extiende US1 pero es independientemente testeable
- **Historia de Usuario 4 (P3)**: Puede comenzar después de Foundational (Phase 2) - Extiende US1 pero es independientemente testeable
- **Historia de Usuario 5 (P3)**: Puede comenzar después de Foundational (Phase 2) - Extiende US2 pero es independientemente testeable

### Dentro de Cada Historia de Usuario

- Componentes base antes de lógica de negocio
- Lógica de negocio antes de integraciones
- Implementación central antes de casos edge
- Historia completa antes de pasar a siguiente prioridad

### Oportunidades de Paralelización

- Todas las tareas de Setup marcadas [P] pueden ejecutarse en paralelo
- Todas las tareas de Foundational marcadas [P] pueden ejecutarse en paralelo (dentro de Phase 2)
- Una vez que Foundational phase se completa, todas las historias de usuario pueden comenzar en paralelo (si hay capacidad de equipo)
- Todas las tareas dentro de una historia de usuario marcadas [P] pueden ejecutarse en paralelo
- Diferentes historias de usuario pueden ser trabajadas en paralelo por diferentes miembros del equipo
- Todas las tareas de Animaciones marcadas [P] pueden ejecutarse en paralelo
- Todas las tareas de Accesibilidad marcadas [P] pueden ejecutarse en paralelo
- Todas las tareas de Documentación marcadas [P] pueden ejecutarse en paralelo

---

## Ejemplo Paralelo: Historia de Usuario 1

```bash
# Lanzar todas las tareas [P] de US1 juntas:
Tarea: "Crear componente LoginForm en components/shared/LoginForm.tsx con estructura básica"
Tarea: "Integrar React Hook Form en LoginForm con esquema Zod de validación"

# Después, tareas secuenciales:
Tarea: "Implementar lógica de submit en LoginForm"
Tarea: "Implementar manejo de respuesta exitosa"
# etc.
```

---

## Estrategia de Implementación

### MVP Primero (Solo Historia de Usuario 1)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (CRÍTICO - bloquea todas las historias)
3. Completar Phase 3: Historia de Usuario 1
4. **DETENER Y VALIDAR**: Probar Historia de Usuario 1 independientemente
5. Desplegar/demo si está listo

### Entrega Incremental

1. Completar Setup + Foundational → Fundación lista
2. Agregar Historia de Usuario 1 → Probar independientemente → Desplegar/Demo (¡MVP!)
3. Agregar Historia de Usuario 2 → Probar independientemente → Desplegar/Demo
4. Agregar Historia de Usuario 3 → Probar independientemente → Desplegar/Demo
5. Agregar Historia de Usuario 4 → Probar independientemente → Desplegar/Demo
6. Agregar Historia de Usuario 5 → Probar independientemente → Desplegar/Demo
7. Agregar Animaciones → Desplegar/Demo
8. Agregar Accesibilidad → Desplegar/Demo
9. Cada historia agrega valor sin romper historias previas

### Estrategia de Equipo Paralelo

Con múltiples desarrolladores:

1. Equipo completa Setup + Foundational juntos
2. Una vez que Foundational está listo:
   - Desarrollador A: Historia de Usuario 1 + 2
   - Desarrollador B: Historia de Usuario 3 + 4
   - Desarrollador C: Historia de Usuario 5 + Animaciones
   - Desarrollador D: Accesibilidad + Documentación
3. Las historias se completan e integran independientemente

---

## Notas

- Tareas [P] = archivos diferentes, sin dependencias
- Etiqueta [Story] mapea tarea a historia de usuario específica para trazabilidad
- Cada historia de usuario debe ser independientemente completable y testeable
- Hacer commit después de cada tarea o grupo lógico
- Detenerse en cualquier checkpoint para validar historia independientemente
- Evitar: tareas vagas, conflictos en mismo archivo, dependencias cross-story que rompan independencia
- Todos los comentarios de código deben estar en español (constitución)
- Todos los mensajes de commit deben estar en español (constitución)

---

## Resumen de Tareas

**Total de Tareas**: 66
- **Phase 1 (Setup)**: 7 tareas
- **Phase 2 (Foundational)**: 8 tareas
- **Phase 3 (US1 - P1)**: 8 tareas 🎯 MVP
- **Phase 4 (US2 - P2)**: 6 tareas
- **Phase 5 (US3 - P2)**: 6 tareas
- **Phase 6 (US4 - P3)**: 5 tareas
- **Phase 7 (US5 - P3)**: 7 tareas
- **Phase 8 (Animaciones)**: 7 tareas
- **Phase 9 (Accesibilidad)**: 6 tareas
- **Phase 10 (Documentación)**: 6 tareas

**Tareas Paralelizables**: 35 tareas marcadas con [P]

**Alcance MVP Sugerido**: Phase 1 + Phase 2 + Phase 3 (Historia de Usuario 1) = 23 tareas
