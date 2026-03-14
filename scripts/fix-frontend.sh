#!/bin/bash
# VoxIA Frontend - Fix Dependencies Script
# This script helps rebuild the frontend and install dependencies correctly

set -e

echo "🐳 VoxIA Frontend Fix Script"
echo "=============================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if docker-compose is running
echo "📋 Checking Docker status..."
if ! docker ps &> /dev/null; then
    echo -e "${RED}✗ Docker daemon is not running${NC}"
    echo "  Please start Docker Desktop"
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Step 1: Stop frontend
echo "🛑 Stopping frontend container..."
docker-compose stop frontend || true
echo -e "${GREEN}✓ Frontend stopped${NC}"
echo ""

# Step 2: Remove frontend container
echo "🗑️  Removing frontend container..."
docker-compose rm -f frontend || true
echo -e "${GREEN}✓ Frontend container removed${NC}"
echo ""

# Step 3: Rebuild frontend without cache
echo "🏗️  Rebuilding frontend image (this may take a few minutes)..."
docker-compose build --no-cache frontend
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend image built successfully${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi
echo ""

# Step 4: Start frontend
echo "🚀 Starting frontend container..."
docker-compose up -d frontend
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend started${NC}"
else
    echo -e "${RED}✗ Failed to start frontend${NC}"
    exit 1
fi
echo ""

# Step 5: Wait for npm ci to complete
echo "⏳ Waiting for npm ci to complete (this may take 1-2 minutes)..."
sleep 10

# Step 6: Check health
echo "🏥 Checking health status..."
for i in {1..30}; do
    if docker-compose exec frontend npm list next &> /dev/null; then
        echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}⚠️  Still installing... check logs with: docker-compose logs -f frontend${NC}"
    else
        echo -n "."
        sleep 2
    fi
done
echo ""

# Step 7: Show logs
echo "📖 Last 20 lines of frontend logs:"
echo "=============================="
docker-compose logs --tail 20 frontend
echo ""

echo -e "${GREEN}✓ Frontend rebuild complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Visit http://localhost:3000"
echo "  2. If errors persist, check logs: docker-compose logs -f frontend"
echo "  3. If you still see 'Cannot find module' errors, you may need to:"
echo "     - Clear VS Code cache: Restart TypeScript server"
echo "     - Run: docker-compose down -v && docker-compose build --no-cache && docker-compose up -d"
echo ""
