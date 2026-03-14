# 🐛 VoxIA Frontend - Troubleshooting Guide

## Problemas Comunes y Soluciones

### ❌ Error: "Cannot find module 'next'"

```
Cannot find module 'next' or its corresponding type declarations.
```

**Causa:** `node_modules` no está instalado en el contenedor.

**Soluciones:**

#### Opción 1: Reconstruir (Recomendado)
```bash
docker-compose down frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

#### Opción 2: Usar script helper
```bash
chmod +x scripts/fix-frontend.sh
./scripts/fix-frontend.sh
```

#### Opción 3: Manual
```bash
# En el contenedor
docker-compose exec frontend sh
cd /app
npm ci  # Instala exactamente las versiones del package-lock.json
exit
```

---

### ❌ Error: "JSX element implicitly has type 'any'"

```
JSX element implicitly has type 'any' because no interface 'JSX.IntrinsicElements' exists.
This JSX tag requires the module path 'react/jsx-runtime' to exist
```

**Causa:** React y tipos de TypeScript no están instalados.

**Solución:**
```bash
docker-compose down frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend

# Si persiste: Reiniciar TypeScript server en VS Code
# Command palette → "TypeScript: Restart TS Server"
```

---

### ❌ Error: "Cannot find module 'sonner'"

```
Cannot find module 'sonner' or its corresponding type declarations.
```

**Causa:** Dependencia de notificaciones no instalada.

**Solución:**

#### Opción 1: Dentro del contenedor
```bash
docker-compose exec frontend npm install sonner
```

#### Opción 2: Actualizar package.json y reconstruir
```bash
# Verificar que sonner esté en package.json
grep "sonner" frontend/package.json

# Si no, agregarlo
npm install sonner  # LOCAL (assumes local node)

# Luego reconstruir
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

---

### ❌ Error: "Cannot find namespace 'React'"

```
Cannot find namespace 'React'.
```

**Causa:** Tipos de React no están disponibles.

**Solución:**
```bash
# Asegurar que tengas estas líneas en tsconfig.json:
cat frontend/tsconfig.json | grep -A 5 '"jsx"'
# Debe mostrar: "jsx": "preserve"

# Reconstruir
docker-compose down -v frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

---

## 🔍 Diagnosis Steps

### 1. Check Container Status
```bash
docker-compose ps frontend
# Estado debe ser: Up
```

### 2. Check Logs
```bash
docker-compose logs -f frontend
# Ver si npm ci terminó exitosamente
```

### 3. Verify Dependencies Installed
```bash
docker-compose exec frontend ls -la node_modules/ | head -20
# Debe haber muchos módulos

docker-compose exec frontend npm list next
# Debe mostrar: next@16.1.6
```

### 4. Check TypeScript Compilation
```bash
docker-compose exec frontend npm run check
# Debe compilar sin errores
```

---

## 🛠️ Manual Fix Procedure

Si los problemas persisten, sigue estos pasos:

```bash
# 1. Stop everything
docker-compose down

# 2. Remove volumes (BE CAREFUL - loses data)
docker-compose down -v

# 3. Clean build
docker-compose build --no-cache

# 4. Start with verbose logging
docker-compose up

# 5. In another terminal, monitor logs
docker-compose logs -f frontend

# 6. Wait 2-3 minutes for npm ci to complete

# 7. If it works, Ctrl+C to stop verbose mode
# Then run in background
docker-compose down
docker-compose up -d
```

---

## 📝 Prevention Tips

### 1. Keep package-lock.json Committed
```bash
# Ensure package-lock.json is in git
git add frontend/package-lock.json
git commit -m "Lock frontend dependencies"
```

### 2. Rebuild After Dependency Changes
```bash
# If you modify frontend/package.json:
docker-compose build --no-cache frontend
docker-compose restart frontend
```

### 3. Use Docker Volumes Correctly
```yaml
# docker-compose.yml should have:
volumes:
  - ./frontend:/app      # Code sync
  - /app/node_modules   # Docker's node_modules (not host)
  - /app/.next          # Next build cache
```

### 4. Clear IDE Cache
```bash
# VS Code
Ctrl+Shift+P → "Developer: Reload Window"
# Or restart VS Code entirely
```

---

## 🚨 Nuclear Option (Last Resort)

If nothing works:

```bash
# Remove ALL Docker resources
docker system prune -a --volumes

# Rebuild from scratch
cd /Users/andresrz/app-vox-ia
docker-compose build --no-cache
docker-compose up -d

# This will take 5-10 minutes but should fix everything
```

---

## ✅ Verification Checklist

After applying fixes, verify:

- [ ] `docker-compose ps frontend` shows "Up"
- [ ] `docker-compose logs frontend` shows "compiled client and server successfully"
- [ ] http://localhost:3000 loads without TypeScript errors
- [ ] VS Code shows no red squiggles
- [ ] `docker-compose exec frontend npm list sonner` returns version
- [ ] `docker-compose exec frontend npm test` passes (if applicable)

---

## 📞 Additional Help

**See logs:**
```bash
docker-compose logs -f frontend --tail 100
```

**Exec bash in container:**
```bash
docker-compose exec frontend sh
npm list  # See all installed packages
npm ci --verbose  # Install with verbose output
```

**Check disk space:**
```bash
docker system df  # See Docker usage
du -sh frontend/node_modules  # Frontend node_modules size
```

---

**Last Updated:** March 14, 2026
