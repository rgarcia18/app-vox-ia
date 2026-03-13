# Especificación de Funcionalidad: Pantalla de Login

**Rama de Funcionalidad**: `001-login-screen`  
**Creado**: 2026-03-07  
**Estado**: Borrador  
**Entrada**: Descripción del usuario: "creemos una pantalla inicial de login, tomando como referencia los siguientes documentos: docs/requirements/interface/login/CU-01-VoxIA-Especificacion.md y login.png"

## Diseño Visual

Referencia: `docs/requirements/interface/login/login.png`

### Layout General

- **Fondo**: gradiente azul claro (`from-blue-50 via-blue-100 to-indigo-50`), animado sutilmente con Framer Motion
- **Tarjeta**: blanca, centrada en pantalla, esquinas redondeadas (`rounded-2xl`), sombra ligera (`shadow-sm`), padding interno `p-8`, ancho máximo `max-w-md`

### Contenido de la tarjeta (de arriba a abajo)

1. **Logo** (centrado):
   - Ícono de micrófono en cuadrado redondeado (`rounded-2xl`) azul (`bg-blue-600`)
   - Título "VoxIA" en negrita, centrado
   - Tagline "Transcripción inteligente de reuniones" en gris claro, centrado

2. **Campo nombre de usuario**:
   - Label: "Ingresa tu nombre de usuario"
   - Input con placeholder `usuario@ejemplo.com`
   - Borde rojo + mensaje de error inline si falla validación

3. **Campo contraseña**:
   - Label: "Contraseña"
   - Input tipo password con botón de alternancia de visibilidad (ícono Eye/EyeOff)
   - Borde rojo + mensaje de error inline si falla validación

4. **Botón "Iniciar sesión"**:
   - Ancho completo (`w-full`)
   - Color primario azul (clase `Button` de shadcn/ui)
   - Estado de carga con spinner (`Loader2`) y texto "Iniciando sesión..."
   - Estado de rate limit con countdown "Espera Xs"

5. **Nota al pie** (centrada, texto pequeño gris):
   - "El acceso está restringido. Contacta al administrador para obtener tus credenciales."

### Animaciones

- Entrada de la tarjeta: `opacity: 0 → 1`, `y: 20 → 0`, duración 500ms `easeOut`
- Salida post-login: `opacity: 1 → 0`, `scale: 1 → 0.95`, duración 300ms
- Respeta `prefers-reduced-motion`: sin animaciones si el usuario lo prefiere

---

## Escenarios de Usuario y Pruebas *(obligatorio)*

### Historia de Usuario 1 - Autenticación Exitosa (Prioridad: P1)

Un usuario con credenciales válidas accede al sistema VoxIA ingresando su nombre de usuario y contraseña en la pantalla de login. El sistema valida sus credenciales y otorga acceso al dashboard de la aplicación.

**Por qué esta prioridad**: Esta es la funcionalidad central de la pantalla de login - sin autenticación exitosa, los usuarios no pueden acceder a ninguna parte del sistema. Esto representa el producto mínimo viable.

**Prueba Independiente**: Puede probarse completamente proporcionando credenciales válidas (nombre de usuario y contraseña), enviando el formulario, y verificando la redirección exitosa al dashboard con el estado de autenticación apropiado.

**Escenarios de Aceptación**:

1. **Dado** que un usuario está en la pantalla de login con campos vacíos, **Cuando** ingresa nombre de usuario y contraseña válidos y envía, **Entonces** es autenticado y redirigido al dashboard
2. **Dado** que un usuario está en la pantalla de login, **Cuando** ingresa credenciales válidas y presiona Enter en cualquier campo, **Entonces** el formulario se envía y es autenticado
3. **Dado** que un usuario inicia sesión exitosamente, **Cuando** navega de vuelta a la página de login, **Entonces** es automáticamente redirigido al dashboard (ya autenticado)

---

### Historia de Usuario 2 - Manejo de Credenciales Inválidas (Prioridad: P2)

Un usuario intenta iniciar sesión con nombre de usuario o contraseña incorrectos. El sistema proporciona retroalimentación clara sobre el fallo de autenticación sin revelar cuál credencial fue incorrecta (mejor práctica de seguridad).

**Por qué esta prioridad**: El manejo de errores es crítico para la experiencia de usuario y seguridad. Los usuarios necesitan retroalimentación clara cuando la autenticación falla, pero el sistema no debe filtrar información sobre cuál credencial fue incorrecta.

**Prueba Independiente**: Puede probarse intentando login con varias combinaciones de credenciales inválidas y verificando que se muestren mensajes de error apropiados sin revelar detalles de seguridad.

**Escenarios de Aceptación**:

1. **Dado** que un usuario está en la pantalla de login, **Cuando** ingresa un nombre de usuario o contraseña inválidos y envía, **Entonces** ve un mensaje de error genérico "Usuario o contraseña incorrectos" y el campo de contraseña se limpia
2. **Dado** que un usuario recibió un error de autenticación, **Cuando** se muestra el error, **Entonces** el foco regresa automáticamente al campo de contraseña para facilitar el reintento
3. **Dado** que un usuario ingresa credenciales inválidas, **Cuando** aparece el error, **Entonces** el botón de login regresa a su estado activo permitiendo reintento inmediato

---

### Historia de Usuario 3 - Validación de Formulario y Guía al Usuario (Prioridad: P2)

Un usuario interactúa con el formulario de login y recibe retroalimentación de validación en tiempo real para asegurar que proporcione credenciales con formato apropiado antes del envío.

**Por qué esta prioridad**: La validación del lado del cliente mejora la experiencia de usuario al detectar errores tempranamente y proporcionar retroalimentación inmediata, reduciendo la frustración y la carga del servidor.

**Prueba Independiente**: Puede probarse interactuando con los campos del formulario (ingresando datos inválidos, dejando campos vacíos, etc.) y verificando que los mensajes de validación apropiados aparezcan en los momentos correctos.

**Escenarios de Aceptación**:

1. **Dado** que un usuario está en la pantalla de login, **Cuando** ambos campos están vacíos, **Entonces** el botón de envío está deshabilitado
2. **Dado** que un usuario está llenando el campo de nombre de usuario, **Cuando** deja el campo (blur) con menos de 3 caracteres, **Entonces** aparece un mensaje de error en línea: "Mínimo 3 caracteres"
3. **Dado** que un usuario ha llenado ambos campos con datos válidos, **Cuando** la validación pasa, **Entonces** el botón de envío se habilita con retroalimentación visual
4. **Dado** que un usuario ingresa caracteres inválidos en el nombre de usuario, **Cuando** deja el campo (blur), **Entonces** aparece un mensaje de error: "Usuario inválido"

---

### Historia de Usuario 4 - Alternancia de Visibilidad de Contraseña (Prioridad: P3)

Un usuario quiere verificar que escribió su contraseña correctamente antes de enviar. Puede alternar la visibilidad de la contraseña para ver los caracteres que ingresó.

**Por qué esta prioridad**: Esta es una mejora de usabilidad que ayuda a prevenir errores de tipeo pero no es crítica para la funcionalidad central de autenticación.

**Prueba Independiente**: Puede probarse haciendo clic en el ícono de ojo en el campo de contraseña y verificando que el texto de la contraseña alterna entre estados oculto y visible.

**Escenarios de Aceptación**:

1. **Dado** que un usuario ha ingresado una contraseña, **Cuando** hace clic en el ícono de ojo, **Entonces** la contraseña se vuelve visible como texto plano
2. **Dado** que la contraseña es visible, **Cuando** hace clic en el ícono de ojo nuevamente, **Entonces** la contraseña regresa al estado oculto
3. **Dado** que un usuario alterna la visibilidad de la contraseña, **Cuando** cambia el estado, **Entonces** el ícono se actualiza apropiadamente (Eye vs EyeOff) con etiquetas ARIA apropiadas

---

### Historia de Usuario 5 - Protección contra Limitación de Tasa (Prioridad: P3)

Un usuario o sistema automatizado realiza demasiados intentos fallidos de login. El sistema bloquea temporalmente intentos adicionales para prevenir ataques de fuerza bruta.

**Por qué esta prioridad**: Característica de seguridad que protege contra ataques pero no afecta el flujo normal del usuario. La mayoría de usuarios legítimos no encontrarán esto.

**Prueba Independiente**: Puede probarse realizando múltiples intentos fallidos de login en rápida sucesión y verificando que el sistema bloquee intentos adicionales con un temporizador de cuenta regresiva.

**Escenarios de Aceptación**:

1. **Dado** que un usuario ha realizado demasiados intentos fallidos de login, **Cuando** intenta enviar nuevamente, **Entonces** ve un mensaje de error "Demasiados intentos. Espera unos minutos" y el botón muestra una cuenta regresiva
2. **Dado** que el límite de tasa está activo, **Cuando** la cuenta regresiva llega a cero, **Entonces** el botón de login se vuelve activo nuevamente
3. **Dado** que la limitación de tasa está en efecto, **Cuando** el usuario espera el período de tiempo de espera, **Entonces** puede intentar login nuevamente normalmente

---

### Casos Extremos

- ¿Qué sucede cuando el usuario tiene una cookie de refresh token válida pero el access token ha expirado? El sistema debe refrescar automáticamente el token vía interceptor sin intervención del usuario.
- ¿Qué sucede cuando tanto el access token como el refresh token han expirado? El usuario es automáticamente desconectado y redirigido a la pantalla de login.
- ¿Qué sucede cuando el servidor backend es inalcanzable o se agota el tiempo de espera? El usuario ve un mensaje de error claro: "No pudimos conectar con el servidor" sin ser bloqueado.
- ¿Qué sucede cuando el usuario navega directamente a una ruta protegida sin autenticación? El middleware lo redirige a la pantalla de login.
- ¿Qué sucede cuando el usuario ya está autenticado y navega a la página de login? El middleware lo redirige al dashboard.
- ¿Qué sucede cuando el usuario envía el formulario mientras ya se está enviando? El botón está deshabilitado durante el envío para prevenir solicitudes duplicadas.
- ¿Qué sucede cuando el nombre de usuario contiene caracteres especiales permitidos por el sistema? La regex de validación acepta caracteres válidos: `a-zA-Z0-9._@-`
- ¿Qué sucede cuando la sesión del usuario expira mientras está usando la aplicación? El interceptor axios intenta automáticamente refrescar el token; si eso falla, el usuario es desconectado y redirigido al login.

## Requerimientos *(obligatorio)*

### Requerimientos Funcionales

- **FR-001**: El sistema DEBE mostrar un formulario de login con campos de nombre de usuario y contraseña como punto de entrada a la aplicación
- **FR-002**: El sistema DEBE validar el formato del nombre de usuario (mínimo 3 caracteres, máximo 50 caracteres, solo alfanuméricos más caracteres `._@-`)
- **FR-003**: El sistema DEBE validar el formato de la contraseña (mínimo 6 caracteres, máximo 100 caracteres)
- **FR-004**: El sistema DEBE deshabilitar el botón de envío cuando los campos del formulario estén vacíos o contengan errores de validación
- **FR-005**: El sistema DEBE realizar validación en eventos blur de campos, no mientras el usuario está escribiendo activamente
- **FR-006**: El sistema DEBE mostrar mensajes de error en línea debajo de los campos cuando la validación falla
- **FR-007**: El sistema DEBE autenticar usuarios enviando credenciales al endpoint de autenticación del backend
- **FR-008**: El sistema DEBE almacenar el access token en memoria (estado de aplicación) únicamente, nunca en almacenamiento del navegador
- **FR-009**: El sistema DEBE aceptar el refresh token como una cookie httpOnly establecida por el backend
- **FR-010**: El sistema DEBE redirigir usuarios autenticados al dashboard tras login exitoso
- **FR-011**: El sistema DEBE mostrar un mensaje de error genérico "Usuario o contraseña incorrectos" para intentos de autenticación fallidos sin revelar cuál credencial fue incorrecta
- **FR-012**: El sistema DEBE limpiar el campo de contraseña y devolver el foco a él después de un fallo de autenticación
- **FR-013**: El sistema DEBE proporcionar un botón de alternancia de visibilidad de contraseña que cambie entre texto oculto y visible
- **FR-014**: El sistema DEBE mostrar un estado de carga en el botón de envío durante solicitudes de autenticación
- **FR-015**: El sistema DEBE manejar respuestas de limitación de tasa del backend mostrando un temporizador de cuenta regresiva y deshabilitando el formulario
- **FR-016**: El sistema DEBE manejar errores del servidor y fallos de red con mensajes de error amigables apropiados
- **FR-017**: El sistema DEBE redirigir automáticamente usuarios ya autenticados desde la página de login al dashboard
- **FR-018**: El sistema DEBE mostrar el logo de VoxIA y el tagline "Transcripción inteligente de reuniones" en la pantalla de login
- **FR-019**: El sistema DEBE proporcionar retroalimentación visual para estados de foco de campos del formulario
- **FR-020**: El sistema DEBE soportar envío de formulario vía tecla Enter desde cualquier campo
- **FR-021**: El sistema DEBE incluir una nota informando a los usuarios que el acceso está restringido y deben contactar al administrador para obtener credenciales
- **FR-022**: El sistema NO DEBE proporcionar flujos de registro o recuperación de contraseña (los usuarios son gestionados por administradores)
- **FR-023**: El sistema DEBE implementar animaciones de entrada suaves cuando la pantalla de login carga
- **FR-024**: El sistema DEBE implementar animaciones de salida suaves al transicionar al dashboard después de login exitoso
- **FR-025**: El sistema DEBE cumplir con estándares de accesibilidad WCAG 2.1 AA incluyendo etiquetas ARIA apropiadas, navegación por teclado, y gestión de foco

### Entidades Clave

- **Usuario**: Representa un usuario autenticado con atributos incluyendo identificador único, nombre de usuario, y nombre para mostrar. Los usuarios son pre-creados por administradores del sistema.
- **Sesión de Autenticación**: Representa una sesión de usuario activa con access token (corta duración, almacenado en memoria) y refresh token (larga duración, almacenado como cookie httpOnly).
- **Credenciales de Login**: Par de nombre de usuario y contraseña enviado para autenticación. Validado tanto en cliente como en servidor.

## Criterios de Éxito *(obligatorio)*

### Resultados Medibles

- **SC-001**: Los usuarios pueden completar el proceso de login en menos de 10 segundos desde que llegan a la página hasta alcanzar el dashboard (asumiendo credenciales válidas y condiciones normales de red)
- **SC-002**: La validación del formulario proporciona retroalimentación inmediata dentro de 200ms de eventos blur de campos
- **SC-003**: El 100% de los errores de autenticación muestran mensajes amigables sin exponer detalles de seguridad
- **SC-004**: La pantalla de login es completamente navegable por teclado con orden de tabulación: nombre de usuario → contraseña → alternancia de visibilidad → botón de envío
- **SC-005**: Todos los elementos interactivos cumplen con ratio de contraste mínimo de 4.5:1 para cumplimiento WCAG AA
- **SC-006**: La pantalla de login carga y muestra animaciones de entrada dentro de 1 segundo en conexiones de banda ancha estándar
- **SC-007**: Los usuarios con credenciales válidas se autentican exitosamente en el primer intento el 95% del tiempo (excluyendo errores de tipeo del usuario)
- **SC-008**: La protección de limitación de tasa se activa después de intentos fallidos excesivos y proporciona retroalimentación clara de cuenta regresiva a los usuarios
- **SC-009**: El sistema maneja graciosamente fallos de red y errores del servidor con mensajería apropiada al usuario el 100% del tiempo
- **SC-010**: Los usuarios autenticados son automáticamente redirigidos desde la página de login al dashboard dentro de 500ms