# Shared base stage
FROM node:22-alpine AS base

WORKDIR /app

# Accept build arguments for environment configuration
ARG NEXT_PUBLIC_API_URL=http://localhost:8000

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Copiar archivos de dependencias
COPY package.json package-lock.json* ./

# Instalar dependencias (con devDependencies para build)
RUN npm ci

# Copiar código fuente
COPY . .

# Development stage
FROM base AS development

ENV NODE_ENV=development \
    NEXT_TELEMETRY_DISABLED=1

EXPOSE 3000

CMD ["npm", "run", "dev"]

# Build de la aplicación
FROM base AS builder

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# Runtime stage
FROM node:22-alpine AS production

WORKDIR /app

# Instalar solo dependencias de producción
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# Copiar build del builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

# Crear usuario no-root
RUN addgroup -g 1001 appuser && adduser -D -u 1001 -G appuser appuser
USER appuser

# Variables de entorno
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Puerto
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

# Comando para correr la aplicación
CMD ["npm", "start"]
