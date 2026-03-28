# CI/CD Pipeline — VoxIA

## Descripción general

El pipeline está implementado en GitLab CI/CD mediante el archivo `.gitlab-ci.yml` en la raíz del repositorio. Se compone de **3 stages** que se ejecutan de forma secuencial: `test → build → deploy`.

---

## Estructura del pipeline

```
test:backend  ──►  build:backend  ──►  deploy:backend
test:frontend ──►  build:frontend ──►  deploy:frontend
```

Cada rama (backend / frontend) es completamente independiente. Los jobs solo corren si hay cambios relevantes en su respectiva carpeta.

---

## Stage 1 — Test

### `test:backend`
- **Imagen:** `python:3.11-slim`
- **Qué hace:** instala dependencias con `uv` y ejecuta los tests unitarios con `pytest tests/unit/ -v`
- **Cuándo corre:** cuando hay cambios en `backend/**` o en `.gitlab-ci.yml`, en ramas `main`/`master` o en merge requests

### `test:frontend`
- **Imagen:** `node:20-alpine`
- **Qué hace:** instala dependencias con `npm install` y ejecuta el linter con `npm run lint`
- **Cuándo corre:** cuando hay cambios en `frontend/**` o en `.gitlab-ci.yml`, en ramas `main`/`master` o en merge requests

**Optimización:** ambos jobs usan caché de dependencias (`.uv-cache/` para Python, `node_modules/` para Node) para acelerar las ejecuciones siguientes.

---

## Stage 2 — Build

### `build:backend` y `build:frontend`
- **Imagen:** `docker:24` con servicio `docker:24-dind` (Docker-in-Docker)
- **Qué hace:**
  1. Se autentica en Docker Hub
  2. Construye la imagen Docker usando `--cache-from :latest` para aprovechar capas previas
  3. Publica la imagen con **dos tags**:
     - `:{commit_sha}` — tag inmutable que identifica exactamente qué commit se deployó
     - `:latest` — tag mutable que siempre apunta a la versión más reciente
- **Cuándo corre:** solo en pushes a `main`/`master` (no en merge requests)

---

## Stage 3 — Deploy

### `deploy:backend` y `deploy:frontend`
- **Imagen:** `alpine:latest`
- **Qué hace:**
  1. Instala `openssh-client` y carga la llave SSH privada del servidor (variable `DO_SSH_PRIVATE_KEY`)
  2. Copia el archivo `docker-compose.prod.yml` al servidor vía `scp`
  3. Por SSH ejecuta en el servidor:
     - `docker login` en Docker Hub
     - `docker pull` de la imagen recién construida
     - `docker compose up -d --no-build <servicio>` — reinicia **solo el servicio afectado**
     - `docker image prune -f` — limpia imágenes huérfanas para no consumir disco
- **Cuándo corre:** solo si el job de `build` correspondiente completó exitosamente (`needs`)

### Gestión de tags en deploy parcial
Cuando solo cambia un servicio, el otro ya está corriendo en producción con su imagen `latest`. Para evitar errores de imagen no encontrada, cada deploy pasa tags independientes:

| Deploy      | BACKEND_TAG   | FRONTEND_TAG  |
|-------------|---------------|---------------|
| backend     | `$IMAGE_TAG`  | `latest`      |
| frontend    | `latest`      | `$IMAGE_TAG`  |

---

## Filtros por carpeta (deploy selectivo)

Los tres escenarios posibles:

| Cambios detectados       | Jobs que corren                                              |
|--------------------------|--------------------------------------------------------------|
| Solo `backend/`          | `test:backend → build:backend → deploy:backend`             |
| Solo `frontend/`         | `test:frontend → build:frontend → deploy:frontend`          |
| Ambas carpetas           | Los 6 jobs corren en paralelo dentro de cada stage          |

Si el cambio es en `.gitlab-ci.yml` (u otro archivo fuera de esas carpetas), corren **todos los jobs** ya que el pipeline en sí se considera un cambio global.

---

## Variables de entorno requeridas (GitLab CI/CD Settings)

| Variable            | Descripción                                      |
|---------------------|--------------------------------------------------|
| `DOCKERHUB_USER`    | Usuario de Docker Hub                            |
| `DOCKERHUB_TOKEN`   | Token de acceso de Docker Hub                    |
| `DO_SSH_PRIVATE_KEY`| Llave SSH privada para conectarse al servidor    |
| `DO_HOST`           | IP o dominio del servidor de producción          |
| `DO_USER`           | Usuario SSH del servidor                         |

---

## Infraestructura de producción

- **Servidor:** Droplet en DigitalOcean
- **Orquestación:** Docker Compose (`docker-compose.prod.yml`)
- **Backend:** `http://<servidor>:8000`
- **Frontend:** `http://<servidor>:3000`

---

## Nota — Push a múltiples repositorios

El repositorio local está configurado con un remote llamado `all` que apunta simultáneamente a GitHub y GitLab. Para subir cambios a ambos con un solo comando:

```bash
git push all master
```

Esto equivale a hacer push a:
- `https://github.com/rgarcia18/app-vox-ia.git`
- `git@gitlab.com:rgarcia-uao/app-vox-ia.git`

El remote `origin` apunta solo a GitHub y se puede usar para operaciones de fetch/pull normales.
