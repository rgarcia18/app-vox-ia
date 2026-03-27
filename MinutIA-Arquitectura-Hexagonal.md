# MinutIA Backend — Guía de Arquitectura Hexagonal
### Documento de referencia para agente de codificación (Claude Code)

---

## Propósito del documento

Este documento define la arquitectura hexagonal del backend de MinutIA.
El agente debe leerlo antes de crear, modificar o revisar cualquier archivo
del proyecto. Cada decisión de ubicación de código debe justificarse
contra estas definiciones.

---

## Stack tecnológico obligatorio

```
Lenguaje:       Python 3.11+
Framework API:  FastAPI 0.111+
ORM:            SQLModel + Alembic
Auth:           python-jose + passlib (bcrypt)
Config:         pydantic-settings
Cola:           Celery 5+ con Redis 7
Transcripción:  faster-whisper (INT8 en CPU)
Resumen:        FLAN-T5 Base (google/flan-t5-base)
Storage local:  aiofiles
Export:         ReportLab
```

---

## Estructura de carpetas

```
minutia-backend/
├── app/
│   ├── domain/
│   │   ├── entities/
│   │   ├── value_objects/
│   │   ├── ports/
│   │   │   ├── inbound/
│   │   │   └── outbound/
│   │   │       ├── repositories/
│   │   │       ├── providers/
│   │   │       └── services/
│   │   ├── use_cases/
│   │   └── exceptions/
│   │
│   ├── adapters/
│   │   ├── inbound/
│   │   │   ├── http/
│   │   │   │   ├── routers/
│   │   │   │   ├── schemas/
│   │   │   │   ├── middleware/
│   │   │   │   └── mappers/
│   │   │   └── workers/
│   │   │       └── mappers/
│   │   │
│   │   └── outbound/
│   │       ├── ai/
│   │       │   ├── whisper/
│   │       │   └── flan/
│   │       ├── persistence/
│   │       │   ├── models/
│   │       │   ├── repositories/
│   │       │   └── mappers/
│   │       ├── storage/
│   │       ├── export/
│   │       ├── queue/
│   │       └── auth/
│   │
│   └── infrastructure/
│       ├── config/
│       ├── container/
│       ├── logging/
│       └── exceptions/
│
├── main.py
├── alembic/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── scripts/
```

---

## Definición y propósito de cada paquete

---

### `domain/` — El núcleo del sistema

**Regla absoluta:** este paquete NO importa nada externo.
Cero imports de FastAPI, SQLModel, Celery, Whisper, Redis o cualquier
librería de terceros. Solo Python estándar.

---

#### `domain/entities/`

**Qué contiene:** objetos de negocio que tienen identidad propia.
Son `@dataclass` puros de Python.

**Propósito:** representar los conceptos centrales del negocio:
un usuario, una sesión de reunión, un chunk de audio, una transcripción,
un resumen, una tarea extraída. Estos objetos son los que viajan
entre capas del sistema.

**Regla:** nunca heredan de SQLModel, Pydantic ni ninguna librería.

---

#### `domain/value_objects/`

**Qué contiene:** objetos inmutables que describen características
sin identidad propia. Principalmente `Enum` y `frozen dataclass`.

**Propósito:** tipificar de forma segura los estados y categorías
del sistema: `SessionStatus`, `SessionType`, `Language`, `AudioFormat`,
`ChunkStatus`. Evitan el uso de strings mágicos en el código.

---

#### `domain/ports/inbound/`

**Qué contiene:** interfaces `ABC` que definen los **casos de uso**
que el dominio expone hacia el exterior.

**Propósito:** son los contratos que los adaptadores de entrada
(HTTP, workers) deben invocar. Definen el "qué hace el sistema"
sin decir "cómo lo hace". Un router de FastAPI nunca llama
directamente a un servicio — siempre llama a un puerto inbound.

---

#### `domain/ports/outbound/repositories/`

**Qué contiene:** interfaces `ABC` para operaciones de persistencia.

**Propósito:** definen el contrato que la base de datos debe cumplir
desde la perspectiva del dominio. El dominio dice "necesito guardar
una sesión y buscarla por ID" — cómo se hace en SQL es problema
del adaptador. Permite cambiar de SQLite a PostgreSQL sin tocar
el dominio.

---

#### `domain/ports/outbound/providers/`

**Qué contiene:** interfaces `ABC` para servicios externos de IA,
storage, autenticación y cola de mensajes.

**Propósito:** definen los contratos de `TranscriptionProvider`,
`SummarizationProvider`, `StorageProvider`, `QueueProvider`,
`AuthTokenProvider`. El dominio dice "necesito transcribir este
audio" — si lo hace Whisper, Google Speech o AWS Transcribe
es problema del adaptador. Permite cambiar de modelo sin tocar
el dominio.

---

#### `domain/ports/outbound/services/`

**Qué contiene:** interfaces `ABC` para servicios de dominio
que encapsulan lógica técnica transversal.

**Propósito:** contratos para `AudioProcessorService`
(conversión FFmpeg) y `TextChunkerService` (dividir texto
largo para FLAN-T5). Son servicios de soporte al dominio
que necesitan implementación técnica externa.

---

#### `domain/use_cases/`

**Qué contiene:** implementaciones concretas de los puertos
inbound. Son clases Python puras.

**Propósito:** aquí vive toda la lógica de negocio del sistema.
Orquestan el flujo completo: reciben entidades, llaman a puertos
outbound, devuelven resultados. Reciben sus dependencias
por constructor (inyección). Nunca instancian adaptadores
directamente — solo conocen interfaces.

**Ejemplo de responsabilidad:** `UploadAudioUseCase` valida
el archivo, crea la sesión en DB, guarda el audio en storage
y encola la tarea de transcripción — todo esto a través
de puertos, sin saber si la DB es SQLite o PostgreSQL.

---

#### `domain/exceptions/`

**Qué contiene:** jerarquía de excepciones propias del negocio.

**Propósito:** separar los errores de negocio (`SessionNotFoundException`,
`InvalidAudioException`, `TranscriptionException`) de los errores
HTTP. El dominio lanza excepciones de dominio — la capa HTTP
las convierte en códigos HTTP apropiados en `infrastructure/exceptions/`.

---

### `adapters/inbound/` — Reciben el mundo exterior

**Propósito general:** traducen requests del mundo exterior
en llamadas a los casos de uso del dominio. No contienen
lógica de negocio. Son el punto de entrada al sistema.

---

#### `adapters/inbound/http/routers/`

**Qué contiene:** endpoints FastAPI organizados por dominio
funcional (auth, audio, sessions, transcript, summary, export).

**Propósito:** recibir requests HTTP, validar con schemas Pydantic,
extraer dependencias con `Depends()`, llamar al caso de uso
correspondiente, mapear la respuesta al schema HTTP y retornarla.
Un router no contiene lógica de negocio — solo orquesta
la comunicación entre HTTP y el dominio.

---

#### `adapters/inbound/http/schemas/`

**Qué contiene:** modelos Pydantic para requests y responses HTTP.

**Propósito:** definir y validar la forma exacta de los datos
que entran y salen por la API REST. Son específicos para HTTP —
no son las entidades del dominio. Un `LoginRequest` no es un `User`.

---

#### `adapters/inbound/http/middleware/`

**Qué contiene:** middleware FastAPI para CORS, autenticación
y logging de requests.

**Propósito:** interceptar todas las requests antes de que lleguen
a los routers para aplicar lógica transversal: verificar JWT,
configurar CORS, registrar logs de entrada/salida.

---

#### `adapters/inbound/http/mappers/`

**Qué contiene:** funciones puras de conversión.

**Propósito:** convertir entidades del dominio en schemas HTTP
para las responses. Mantienen separados el modelo de dominio
del modelo de la API. Un cambio en la API no obliga a cambiar
la entidad de dominio.

---

#### `adapters/inbound/workers/`

**Qué contiene:** tareas Celery decoradas con `@shared_task`.

**Propósito:** adaptar el sistema de cola de mensajes al dominio.
Cuando Redis dispara una tarea, el worker la recibe, construye
las dependencias necesarias, llama al caso de uso y actualiza
el estado. Los workers son otro tipo de adaptador de entrada,
igual que los routers HTTP, pero activados por cola en lugar
de HTTP.

---

#### `adapters/inbound/workers/mappers/`

**Qué contiene:** funciones que convierten los parámetros
de las tareas Celery en entidades del dominio.

**Propósito:** los mensajes en Redis son diccionarios serializados.
Este mapper los convierte en objetos tipados antes de pasarlos
al caso de uso.

---

### `adapters/outbound/` — Se comunican con el exterior

**Propósito general:** implementan los puertos outbound del dominio.
Contienen el código específico de cada librería o servicio externo.
Son intercambiables sin tocar el dominio.

---

#### `adapters/outbound/ai/whisper/`

**Qué contiene:** implementación de `TranscriptionProvider`
usando faster-whisper.

**Propósito:** encapsular toda la lógica específica de Whisper:
carga del modelo (singleton con `lru_cache`), conversión de audio,
transcripción por segmentos, manejo de errores del modelo.
Incluye dos variantes: procesamiento de archivo completo
y streaming en tiempo real con Whisper-Streaming + VAD.

---

#### `adapters/outbound/ai/flan/`

**Qué contiene:** implementación de `SummarizationProvider`
usando FLAN-T5.

**Propósito:** encapsular toda la lógica de FLAN-T5: carga del modelo,
resumen jerárquico para textos largos, extracción de tareas con
prompt engineering, control de temperatura y beam search.

---

#### `adapters/outbound/persistence/models/`

**Qué contiene:** clases SQLModel con `table=True`.

**Propósito:** definir el esquema de la base de datos.
Son completamente distintos de las entidades del dominio —
existen solo para mapear a tablas SQL. Un cambio en el schema
de la DB no debe afectar las entidades del dominio.

---

#### `adapters/outbound/persistence/repositories/`

**Qué contiene:** implementaciones concretas de los puertos
repository usando SQLModel y sesiones de base de datos.

**Propósito:** ejecutar las queries SQL necesarias para cumplir
los contratos definidos en los puertos. Reciben una sesión DB
por constructor. Usan los mappers para convertir entre modelos
DB y entidades del dominio.

---

#### `adapters/outbound/persistence/mappers/`

**Qué contiene:** funciones puras de conversión bidireccional.

**Propósito:** convertir entre modelos SQLModel (DB) y entidades
del dominio. Mantienen aisladas las dos representaciones.
`SessionModel → MeetingSession` y `MeetingSession → SessionModel`.

---

#### `adapters/outbound/storage/`

**Qué contiene:** implementaciones de `StorageProvider`.

**Propósito:** abstraer el almacenamiento de archivos binarios
(audio, PDFs). `LocalStorageAdapter` guarda en disco local para
desarrollo y Etapa 1. `R2StorageAdapter` guarda en Cloudflare R2
para producción. El dominio no sabe dónde se guardan los archivos.

---

#### `adapters/outbound/export/`

**Qué contiene:** implementaciones de `ExportProvider`.

**Propósito:** generar archivos de salida a partir de los resultados
procesados. `PDFAdapter` usa ReportLab para generar el PDF
estructurado con resumen, puntos clave, tareas y transcripción.
`TXTAdapter` genera el texto plano.

---

#### `adapters/outbound/queue/`

**Qué contiene:** implementación de `QueueProvider` usando Celery.

**Propósito:** encolar tareas de procesamiento asíncrono.
El dominio llama a `queue_provider.enqueue(task, params)` —
no sabe que por debajo hay Celery y Redis.

---

#### `adapters/outbound/auth/`

**Qué contiene:** implementaciones de `AuthTokenProvider`
y el servicio de hash de contraseñas.

**Propósito:** encapsular la generación y verificación de JWT
(python-jose) y el hash de contraseñas (passlib/bcrypt).
El dominio solo conoce el contrato — no sabe qué algoritmo
de firma se usa.

---

### `infrastructure/` — Configuración transversal

**Propósito general:** conectar y configurar todas las piezas
del sistema. No contiene lógica de negocio ni de adaptadores.

---

#### `infrastructure/config/`

**Qué contiene:** clase `Settings` basada en `pydantic-settings`.

**Propósito:** centralizar todas las variables de entorno del sistema
en un único objeto tipado y validado. Es la única fuente de verdad
para configuración. Se accede como singleton en toda la aplicación.

---

#### `infrastructure/container/`

**Qué contiene:** funciones de inyección de dependencias FastAPI.

**Propósito:** este es el punto donde se decide qué implementación
concreta se usa para cada puerto. `get_transcription_provider()`
retorna `WhisperAdapter`. `get_session_repository()` retorna
`SQLSessionRepository`. `get_upload_audio_use_case()` ensambla
el caso de uso con todas sus dependencias.

Para cambiar de Whisper a Google Speech, solo se modifica
`get_transcription_provider()` — ningún otro archivo cambia.
Es el único lugar del sistema que conoce tanto el dominio
como los adaptadores simultáneamente.

---

#### `infrastructure/logging/`

**Qué contiene:** configuración del sistema de logging.

**Propósito:** configurar logging estructurado (JSON) para
producción y logging legible para desarrollo. Define los niveles,
formatos y destinos de los logs del sistema.

---

#### `infrastructure/exceptions/`

**Qué contiene:** handler global de excepciones para FastAPI.

**Propósito:** interceptar las excepciones de dominio antes
de que lleguen al usuario y convertirlas en respuestas HTTP
apropiadas. `SessionNotFoundException → 404`,
`UnauthorizedException → 401`,
`InvalidAudioException → 400`. Mantiene los routers limpios
de lógica de manejo de errores.

---

### `tests/`

---

#### `tests/unit/`

**Qué contiene:** tests de casos de uso y entidades del dominio.

**Propósito:** verificar la lógica de negocio pura usando mocks
de los puertos outbound. No usan DB real, no usan Whisper real,
no hacen llamadas HTTP. Son los tests más rápidos y los más
importantes — validan que el negocio funciona correctamente
independientemente de la infraestructura.

---

#### `tests/integration/`

**Qué contiene:** tests de adaptadores individuales con sus
dependencias reales.

**Propósito:** verificar que los adaptadores funcionan
correctamente con sus librerías: que `WhisperAdapter` transcribe
correctamente, que `SQLSessionRepository` guarda y recupera
datos, que `PDFAdapter` genera un PDF válido. Usan SQLite
en memoria para los tests de DB.

---

#### `tests/e2e/`

**Qué contiene:** tests del flujo completo via HTTP.

**Propósito:** verificar que el sistema funciona end-to-end:
desde el request HTTP hasta la respuesta, pasando por dominio,
adaptadores y DB. Usan el cliente de test de FastAPI.
Son los tests más lentos pero los más cercanos al uso real.

---

### `scripts/`

**Qué contiene:** scripts Python ejecutables directamente.

**Propósito:** tareas operativas que se ejecutan una vez o
periódicamente: poblar usuarios iniciales en la DB antes del
primer despliegue, pre-descargar los modelos Whisper y FLAN-T5
para evitar descarga en el primer request, limpiar archivos
temporales de audio que no fueron eliminados por errores.

---

## Regla de dependencias — Obligatoria

```
El flujo de dependencias es SIEMPRE hacia el centro:

  adapters/ ──────────────► domain/
  infrastructure/ ─────────► domain/
  infrastructure/ ─────────► adapters/

  domain/ NO importa de adapters/ ni infrastructure/
  NUNCA. Sin excepciones.
```

---

## Decisiones de ubicación — Guía rápida

| Situación | Ubicación correcta |
|---|---|
| Nueva entidad de negocio | `domain/entities/` |
| Nuevo estado o categoría | `domain/value_objects/` |
| Nueva operación que el sistema realiza | `domain/ports/inbound/` + `domain/use_cases/` |
| Nueva dependencia externa necesaria | `domain/ports/outbound/providers/` o `repositories/` |
| Nuevo endpoint HTTP | `adapters/inbound/http/routers/` |
| Nuevo modelo de request/response | `adapters/inbound/http/schemas/` |
| Nueva tarea asíncrona | `adapters/inbound/workers/` |
| Nueva integración con IA o servicio externo | `adapters/outbound/` |
| Nueva tabla en la DB | `adapters/outbound/persistence/models/` |
| Nueva variable de entorno | `infrastructure/config/` |
| Cambiar qué implementación se usa | `infrastructure/container/` |
