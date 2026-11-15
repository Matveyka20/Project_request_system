#!/bin/bash
# Quick Startup Script for VPS
# Usage: ./scripts/startup.sh
# Or: docker-compose exec app bash scripts/startup.sh

set -e

# Configuration
APP_PORT="${APP_PORT:-8000}"
APP_DIR="${APP_DIR:-/opt/request-system}"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}[INFO]${NC} Starting Request System services..."

# Navigate to app directory
cd "$APP_DIR"

# Start services
docker-compose up -d

# Wait for services to be healthy
echo -e "${BLUE}[INFO]${NC} Waiting for services to start (10 seconds)..."
sleep 10

# Check health
echo ""
echo -e "${BLUE}[INFO]${NC} Checking application health..."
if curl -s http://localhost:$APP_PORT/health | jq . > /dev/null 2>&1; then
    echo -e "${GREEN}[SUCCESS]${NC} Health check passed!"
else
    echo -e "${BLUE}[INFO]${NC} Health check pending, checking again in 5 seconds..."
    sleep 5
fi

# Display services status
echo ""
echo -e "${BLUE}[INFO]${NC} Services status:"
docker-compose ps

# Display connection information
echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  Request System API Started${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"

SERVER_IP=$(hostname -I | awk '{print $1}')
echo ""
echo -e "Access API at: ${BLUE}http://${SERVER_IP}:${APP_PORT}${NC}"
echo -e "Swagger UI:    ${BLUE}http://${SERVER_IP}:${APP_PORT}/docs${NC}"
echo -e "ReDoc:         ${BLUE}http://${SERVER_IP}:${APP_PORT}/redoc${NC}"
echo ""

echo -e "${BLUE}[INFO]${NC} Useful commands:"
echo "  View logs:     docker-compose logs -f app"
echo "  Check status:  docker-compose ps"
echo "  Stop:          docker-compose down"
echo "  Restart:       docker-compose restart"
echo ""
