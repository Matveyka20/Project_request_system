#!/bin/bash
set -e

# Local Script to Push Code to Remote Server
# Usage: bash scripts/push-to-server.sh <SERVER_IP> <SERVER_USER> [SSH_PORT]
# Example: bash scripts/push-to-server.sh 192.168.1.100 ubuntu 22

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

# Configuration
SERVER_IP="${1:-}"
SERVER_USER="${2:-ubuntu}"
SSH_PORT="${3:-22}"
APP_DIR="/opt/request-system"
LOCAL_DIR="$(pwd)"

# Verify parameters
if [ -z "$SERVER_IP" ]; then
    log_error "Missing SERVER_IP parameter"
    echo "Usage: bash scripts/push-to-server.sh <SERVER_IP> <SERVER_USER> [SSH_PORT]"
    exit 1
fi

# Display banner
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          Push Code to Remote Server Script                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
log_info "Server:     $SERVER_USER@$SERVER_IP:$SSH_PORT"
log_info "App Dir:    $APP_DIR"
log_info "Local Dir:  $LOCAL_DIR"
echo ""

# Test SSH connectivity
log_info "Testing SSH connectivity..."
if ssh -p "$SSH_PORT" -o ConnectTimeout=5 "$SERVER_USER@$SERVER_IP" "echo 'Connected'" >/dev/null 2>&1; then
    log_success "SSH connection established"
else
    log_error "Failed to connect to $SERVER_USER@$SERVER_IP:$SSH_PORT"
    exit 1
fi

# Push code using git
log_info "Pushing code to remote server..."
ssh -p "$SSH_PORT" "$SERVER_USER@$SERVER_IP" << EOF
cd $APP_DIR
git fetch origin
git checkout theodore/develop
git pull origin theodore/develop
echo "Code updated successfully"
EOF

if [ $? -eq 0 ]; then
    log_success "Code pushed successfully"
else
    log_error "Failed to push code"
    exit 1
fi

# Restart services
log_info "Restarting services..."
ssh -p "$SSH_PORT" "$SERVER_USER@$SERVER_IP" << EOF
cd $APP_DIR
docker-compose restart app
sleep 5
echo "Services restarted"
EOF

if [ $? -eq 0 ]; then
    log_success "Services restarted successfully"
else
    log_error "Failed to restart services"
    exit 1
fi

# Verify health
log_info "Verifying deployment health..."
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://$SERVER_IP:8000/health" 2>/dev/null || echo "000")

if [ "$HEALTH_STATUS" = "200" ]; then
    log_success "Health check passed (HTTP $HEALTH_STATUS)"
    echo ""
    log_success "Deployment verification completed!"
    echo ""
    echo "API is running at: http://$SERVER_IP:8000"
    echo "Swagger UI: http://$SERVER_IP:8000/docs"
else
    log_warning "Health check returned HTTP $HEALTH_STATUS (services may still be starting)"
    echo "Please wait and check manually: curl http://$SERVER_IP:8000/health"
fi

echo ""
log_success "Push to server completed!"
