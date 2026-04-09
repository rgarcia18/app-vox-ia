## 🆘 QUICK FIX - Frontend npm Dependencies

### El Problema
Ves errores en VS Code como:
- ❌ "Cannot find module 'next'"
- ❌ "Cannot find namespace 'React'"  
- ❌ "Cannot find module 'sonner'"

**Causa:** Los módulos npm (`node_modules`) no están instalados en el contenedor del frontend.

---

### 🚀 La Solución (3 Pasos)

#### Paso 1: Reconstruir el Frontend
```bash
cd /Users/andresrz/app-vox-ia

docker-compose down frontend  # Detener frontend
docker-compose build --no-cache frontend  # Reconstruir sin caché
```

#### Paso 2: Iniciar el Frontend
```bash
docker-compose up -d frontend  # Iniciar en background
```

#### Paso 3: Esperar e Inspeccionar
```bash
# Espera 30-60 segundos, luego verifica logs:
docker-compose logs -f frontend

# Debes ver algo como:
# > npm ci
# npm notice created a lockfile as package-lock.json
# added XXX packages in XXs
```

---

### ✅ Verificación

Una vez hecho esto, verifica:

```bash
# 1. Chequea que el contenedor esté arriba
docker-compose ps frontend
# Debe mostrar: Up (healthy)

# 2. Verifica que next está instalado
docker-compose exec frontend npm list next

# 3. Abre en el navegador
# http://localhost:3000
# Los errores de TypeScript deben desaparecer
```

---

### 🔧 Si Aún Tiene Errores

Prueba esto:

```bash
# Nuclear option - limpiar y reconstruir TODO
docker-compose down -v  # Borra todas las imágenes y volúmenes
docker-compose build --no-cache  # Reconstruye todo
docker-compose up -d  # Inicia todo
```

---

### 💡 Explicación

El problema ocurre porque:
1. El Dockerfile del frontend necesita ejecutar `npm ci` durante el build
2. O el comando en docker-compose debe correr `npm ci` antes de `npm run dev`
3. Actualmente esto no está sucediendo correctamente

He actualizado el `docker-compose.yml` para que ahora ejecute:
```yaml
command: sh -c "cd /app && npm ci && npm run dev"
```

Esto asegura que `npm ci` (instalar dependencias exactas) se ejecute antes de iniciar el servidor.

---

### 📚 Para Más Ayuda

Consulta: `FRONTEND_TROUBLESHOOTING.md`

Ahí encontrarás:
- ✅ Soluciones detalladas para cada error
- ✅ Pasos de diagnosis
- ✅ Scripts helper
- ✅ Opciones nucleares

---

**¿Still having issues?** Run:
```bash
chmod +x scripts/fix-frontend.sh
./scripts/fix-frontend.sh
```

Este script automatiza todo el proceso de reconstrucción.
