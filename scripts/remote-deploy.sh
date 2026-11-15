#!/bin/bash
set -e

# Remote VPS Deployment Script
# Usage: bash scripts/remote-deploy.sh <SERVER_IP> <SERVER_USER> [SSH_PORT]
# Example: bash scripts/remote-deploy.sh 192.168.1.100 ubuntu 22

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER_IP="${1:-}"
SERVER_USER="${2:-ubuntu}"
SSH_PORT="${3:-22}"
APP_DIR="/opt/request-system"
REPO_URL="https://github.com/Matveyka20/Project_request_system.git"
BRANCH="theodore/develop"
LOG_FILE="deployment-$(date +%Y%m%d_%H%M%S).log"

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}✗${NC} $1" | tee -a "$LOG_FILE"
}

# Verify parameters
if [ -z "$SERVER_IP" ]; then
    log_error "Missing SERVER_IP parameter"
    echo "Usage: bash scripts/remote-deploy.sh <SERVER_IP> <SERVER_USER> [SSH_PORT]"
    exit 1
fi

# Display banner
clear
echo "╔════════════════════════════════════════════════════════════╗"
echo "║      Request System - Remote VPS Deployment Script         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
log_info "Server IP: $SERVER_IP"
log_info "Server User: $SERVER_USER"
log_info "SSH Port: $SSH_PORT"
log_info "App Directory: $APP_DIR"
log_info "Repository: $REPO_URL"
log_info "Branch: $BRANCH"
log_info "Log File: $LOG_FILE"
echo ""

# Test SSH connectivity
log_info "Testing SSH connectivity..."
if ssh -p "$SSH_PORT" -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "echo 'SSH connection successful'" >/dev/null 2>&1; then
    log_success "SSH connection established"
else
    log_error "Failed to connect to $SERVER_USER@$SERVER_IP:$SSH_PORT"
    echo "Please verify:"
    echo "  1. Server IP address is correct"
    echo "  2. SSH port is correct (default: 22)"
    echo "  3. SSH key is configured properly"
    echo "  4. Server is reachable"
    exit 1
fi

# Execute remote deployment
log_info "Starting remote deployment..."
echo ""

ssh -p "$SSH_PORT" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'EOF'
set -e

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

APP_DIR="/opt/request-system"
REPO_URL="https://github.com/Matveyka20/Project_request_system.git"
BRANCH="theodore/develop"

log_info "=== Step 1: System Update ==="
sudo apt-get update && sudo apt-get upgrade -y 2>/dev/null && log_success "System updated"

log_info "=== Step 2: Install Prerequisites ==="
sudo apt-get install -y git curl wget gnupg 2>/dev/null && log_success "Prerequisites installed"

log_info "=== Step 3: Install Docker ==="
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh 2>/dev/null
    sudo sh get-docker.sh 2>/dev/null
    rm get-docker.sh
    sudo usermod -aG docker $USER 2>/dev/null || true
    log_success "Docker installed"
else
    log_warning "Docker already installed"
fi

log_info "=== Step 4: Install Docker Compose ==="
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose 2>/dev/null
    sudo chmod +x /usr/local/bin/docker-compose
    log_success "Docker Compose installed"
else
    log_warning "Docker Compose already installed"
fi

log_info "=== Step 5: Clone Repository ==="
if [ ! -d "$APP_DIR" ]; then
    sudo mkdir -p $APP_DIR
    sudo git clone -b $BRANCH $REPO_URL $APP_DIR 2>/dev/null
    log_success "Repository cloned"
else
    log_warning "Directory exists, pulling latest changes..."
    cd $APP_DIR
    sudo git fetch origin
    sudo git checkout $BRANCH
    sudo git pull origin $BRANCH 2>/dev/null
    log_success "Repository updated"
fi

log_info "=== Step 6: Setup Environment ==="
cd $APP_DIR
if [ ! -f .env ]; then
    if [ -f .env.docker.example ]; then
        sudo cp .env.docker.example .env
        log_success "Environment file created from template"
    else
        log_warning "No environment template found"
    fi
else
    log_warning "Environment file already exists"
fi
sudo chown -R $USER:$USER $APP_DIR 2>/dev/null || true
chmod 600 .env

log_info "=== Step 7: Start Services ==="
cd $APP_DIR
docker-compose up -d 2>/dev/null
log_success "Services started"

log_info "=== Step 8: Wait for Services ==="
sleep 10

log_info "=== Step 9: Verify Deployment ==="
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    log_success "Health check endpoint responding"
else
    log_warning "Health check endpoint not yet responding (may still be starting)"
fi

echo ""
log_success "Remote deployment completed successfully!"
echo ""
echo "Access your application at:"
echo "  • API: http://$(hostname -I | awk '{print $1}'):8000"
echo "  • Swagger: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "Next steps:"
echo "  1. Configure your domain DNS"
echo "  2. Setup Nginx reverse proxy"
echo "  3. Install SSL certificate with Let's Encrypt"
echo "  4. Configure monitoring and backups"

EOF

log_success "Remote deployment completed!"
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                 Deployment Summary                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Server:        $SERVER_USER@$SERVER_IP:$SSH_PORT"
echo "Application:   $APP_DIR"
echo "Repository:    $REPO_URL"
echo "Branch:        $BRANCH"
echo "Status:        ✓ Deployed"
echo ""
echo "Access:"
echo "  • API:       http://$SERVER_IP:8000/docs"
echo "  • Health:    http://$SERVER_IP:8000/health"
echo ""
echo "Log file: $LOG_FILE"
echo ""
log_success "All done!"
