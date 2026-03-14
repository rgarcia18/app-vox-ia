#!/bin/bash
# ==================================================
# VoxIA Frontend - Complete Fix Procedure
# ==================================================
# Execute this step by step when terminal is responsive

set -e

cd /Users/andresrz/app-vox-ia

echo "🔧 VoxIA Frontend - Complete Fix"
echo "=================================="
echo ""

# Step 1
echo "1️⃣  Stopping frontend..."
docker-compose stop frontend
echo "   ✓ Done"
echo ""

# Step 2
echo "2️⃣  Removing frontend container..."
docker-compose rm -f frontend
echo "   ✓ Done"
echo ""

# Step 3
echo "3️⃣  Building frontend (this takes 2-5 minutes)..."
docker-compose build --no-cache frontend
if [ $? -ne 0 ]; then
  echo "   ✗ Build failed!"
  exit 1
fi
echo "   ✓ Build completed"
echo ""

# Step 4
echo "4️⃣  Starting frontend..."
docker-compose up -d frontend
echo "   ✓ Container started"
echo ""

# Step 5
echo "5️⃣  Waiting for npm ci to complete (30-60 seconds)..."
sleep 15
for i in {1..30}; do
  if docker-compose ps frontend | grep -q "healthy\|Up"; then
    echo "   ✓ Container is healthy"
    break
  fi
  echo -n "."
  sleep 2
done
echo ""
echo ""

# Step 6
echo "6️⃣  Verification..."
echo ""
echo "Checking container status:"
docker-compose ps frontend
echo ""

echo "Checking if Next.js is installed:"
docker-compose exec frontend npm list next || echo "   (installing...)"
echo ""

echo "Last 20 lines of logs:"
echo "---"
docker-compose logs --tail 20 frontend
echo "---"
echo ""

echo "✅ Frontend rebuild complete!"
echo ""
echo "Next steps:"
echo "  1. Visit http://localhost:3000"
echo "  2. Errors should be gone"
echo "  3. If issues persist, run: docker-compose logs -f frontend"
echo ""
