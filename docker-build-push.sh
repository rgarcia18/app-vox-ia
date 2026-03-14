#!/bin/bash

# Script para construir y subir imágenes a Docker Hub
# Uso: ./docker-build-push.sh <version>

set -e

DOCKER_USERNAME="arz7"
PROJECT_NAME="voxia"
VERSION=${1:-latest}

echo "🐳 VoxIA Docker Build & Push Script"
echo "===================================="
echo ""
echo "Docker Hub Username: $DOCKER_USERNAME"
echo "Project: $PROJECT_NAME"
echo "Version: $VERSION"
echo ""

# Build Backend
echo "📦 Building backend image..."
docker build -t $DOCKER_USERNAME/$PROJECT_NAME-backend:$VERSION ./backend
docker tag $DOCKER_USERNAME/$PROJECT_NAME-backend:$VERSION $DOCKER_USERNAME/$PROJECT_NAME-backend:latest
echo "✅ Backend image built successfully"
echo ""

# Build Frontend
echo "📦 Building frontend image..."
docker build -t $DOCKER_USERNAME/$PROJECT_NAME-frontend:$VERSION ./frontend
docker tag $DOCKER_USERNAME/$PROJECT_NAME-frontend:$VERSION $DOCKER_USERNAME/$PROJECT_NAME-frontend:latest
echo "✅ Frontend image built successfully"
echo ""

# Login to Docker Hub
echo "🔐 Logging in to Docker Hub..."
docker login
echo "✅ Logged in successfully"
echo ""

# Push Backend
echo "📤 Pushing backend image..."
docker push $DOCKER_USERNAME/$PROJECT_NAME-backend:$VERSION
docker push $DOCKER_USERNAME/$PROJECT_NAME-backend:latest
echo "✅ Backend image pushed successfully"
echo ""

# Push Frontend
echo "📤 Pushing frontend image..."
docker push $DOCKER_USERNAME/$PROJECT_NAME-frontend:$VERSION
docker push $DOCKER_USERNAME/$PROJECT_NAME-frontend:latest
echo "✅ Frontend image pushed successfully"
echo ""

# Summary
echo "======================================"
echo "✅ All images built and pushed!"
echo ""
echo "Backend image tags:"
echo "  - $DOCKER_USERNAME/$PROJECT_NAME-backend:$VERSION"
echo "  - $DOCKER_USERNAME/$PROJECT_NAME-backend:latest"
echo ""
echo "Frontend image tags:"
echo "  - $DOCKER_USERNAME/$PROJECT_NAME-frontend:$VERSION"
echo "  - $DOCKER_USERNAME/$PROJECT_NAME-frontend:latest"
echo ""
echo "Run locally with:"
echo "  docker-compose up"
echo "======================================"
