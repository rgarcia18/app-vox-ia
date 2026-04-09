# 🐳 VoxIA - Docker Setup Guide

## 📋 Prerequisitos

- Docker >= 20.10
- Docker Compose >= 2.0
- Cuenta en [Docker Hub](https://hub.docker.com)

## 🏗️ Estructura Docker

El proyecto incluye:

- **Backend Container**: FastAPI con modelos de ML (Whisper, FLAN-T5)
- **Frontend Container**: Next.js aplicación React
- **Redis Container**: Cache y session storage
- **Docker Compose**: Orquestación de servicios

## 🚀 Quickstart Local

### 1. Construir imágenes localmente

```bash
# Construir todas las imágenes
docker-compose build

# O construir servicios específicos
docker-compose build backend
docker-compose build frontend
```

### 2. Ejecutar los servicios

```bash
# Iniciar todos los servicios en modo detached
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Detener servicios
docker-compose down
```

### 3. Acceder a la aplicación

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Redis**: localhost:6379

## 📤 Subir a Docker Hub

### Prerequisito: Autenticación

```bash
docker login
# Ingresar tu usuario (arz7) y token de acceso
```

> Genera un token en [Docker Hub Settings > Security](https://hub.docker.com/settings/security)

### Opción 1: Script automático (Recomendado)

```bash
# Hacer el script ejecutable
chmod +x docker-build-push.sh

# Ejecutar el script (sin argumento = latest, con argumento = versión específica)
./docker-build-push.sh
./docker-build-push.sh 1.0.0
```

### Opción 2: Comandos manuales

```bash
# Variables
DOCKER_USER="arz7"
VERSION="1.0.0"

# Build backend
docker build -t $DOCKER_USER/voxia-backend:$VERSION ./backend
docker tag $DOCKER_USER/voxia-backend:$VERSION $DOCKER_USER/voxia-backend:latest

# Push backend
docker push $DOCKER_USER/voxia-backend:$VERSION
docker push $DOCKER_USER/voxia-backend:latest

# Build frontend
docker build -t $DOCKER_USER/voxia-frontend:$VERSION ./frontend
docker tag $DOCKER_USER/voxia-frontend:$VERSION $DOCKER_USER/voxia-frontend:latest

# Push frontend
docker push $DOCKER_USER/voxia-frontend:$VERSION
docker push $DOCKER_USER/voxia-frontend:latest
```

## 📊 Monitorear imágenes

```bash
# Listar imágenes locales
docker images | grep voxia

# Ver detalles de una imagen
docker inspect arz7/voxia-backend:latest

# Ver imágenes en Docker Hub (desde el navegador)
# https://hub.docker.com/r/arz7/voxia-backend
# https://hub.docker.com/r/arz7/voxia-frontend
```

## 🔄 Desarrollo con Docker

### Modo desarrollo (con hot-reload)

El `docker-compose.yml` está configurado para desarrollo con:
- Volúmenes montados para code changes
- Comandos con `--reload` para backend
- `npm run dev` para frontend

```bash
docker-compose up
```

### Modo producción

Para producción, edita `docker-compose.yml`:

```yaml
# Cambiar comando para backend (quitar --reload)
command: uvicorn app.main:app --host 0.0.0.0 --port 8000

# Cambiar NODE_ENV para frontend
environment:
  - NODE_ENV=production
```

## 🛠️ Troubleshooting

### Problema: Puerto ya en uso

```bash
# Cambiar puertos en docker-compose.yml
# O matar el proceso que usa el puerto
lsof -i :8000  # Ver qué usa puerto 8000
kill -9 <PID>
```

### Problema: Build lento

```bash
# Limpiar caché de docker
docker builder prune
docker system prune
```

### Problema: Permisos negados en Linux

```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
# Reiniciar sesión
newgrp docker
```

### Problema: Certificados SSL en dev

```bash
# Asegurar que FRONTEND_URL apunta a http (no https) en desarrollo
```

## 📚 Variables de Entorno

Crear archivo `.env.docker` con:

```env
# Backend
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./test.db

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Docker
DOCKER_USERNAME=arz7
```

## 🔒 Seguridad (Producción)

Antes de usar en producción:

1. ✅ Cambiar `SECRET_KEY` a un valor fuerte
2. ✅ Usar PostgreSQL en lugar de SQLite
3. ✅ Configurar HTTPS/SSL
4. ✅ Usar variables de entorno de productión
5. ✅ Implementar rate limiting
6. ✅ Usar reverse proxy (nginx)
7. ✅ Habilitar autenticación de container registry

## 📖 Recursos

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Docker Hub](https://hub.docker.com)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Autor**: VoxIA Team
**Última actualización**: 2026-03-14
