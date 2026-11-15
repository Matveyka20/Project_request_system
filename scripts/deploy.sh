#!/bin/bash
# VPS Deployment Script for Request System API
# This script automates the deployment of the Request System API to a Linux VPS
# Usage: sudo bash deploy.sh
# Or: curl -sSL https://raw.githubusercontent.com/TheodorePrescott821/.../develop/scripts/deploy.sh | sudo bash

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="${REPO_URL:-https://github.com/Matveyka20/Project_request_system.git}"
BRANCH="${BRANCH:-theodore/develop}"
APP_DIR="${APP_DIR:-/opt/request-system}"
APP_USER="${APP_USER:-appuser}"
APP_PORT="${APP_PORT:-8000}"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root. Use: sudo bash deploy.sh"
    fi
}

# Main deployment steps
main() {
    log_info "=========================================="
    log_info "Request System API - VPS Deployment Script"
    log_info "=========================================="
    log_info "Repository: $REPO_URL"
    log_info "Branch: $BRANCH"
    log_info "Installation directory: $APP_DIR"
    log_info "Application port: $APP_PORT"
    log_info ""

    check_root

    # Step 1: System Updates
    log_info "Step 1/9: Updating system packages..."
    apt-get update
    apt-get upgrade -y
    log_success "System packages updated"

    # Step 2: Install Prerequisites
    log_info "Step 2/9: Installing prerequisites..."
    apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        software-properties-common \
        git \
        wget \
        jq
    log_success "Prerequisites installed"

    # Step 3: Install Docker
    log_info "Step 3/9: Installing Docker..."
    
    # Check if Docker is already installed
    if command -v docker &> /dev/null; then
        log_warning "Docker already installed"
    else
        # Add Docker GPG key
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        
        # Add Docker repository
        echo \
            "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
            $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Install Docker
        apt-get update
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        
        # Start Docker service
        systemctl start docker
        systemctl enable docker
        
        log_success "Docker installed and started"
    fi

    # Step 4: Install Docker Compose
    log_info "Step 4/9: Installing Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        log_warning "Docker Compose already installed"
    else
        DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d'"' -f4)
        curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        
        log_success "Docker Compose installed"
    fi

    # Step 5: Create Application Directory
    log_info "Step 5/9: Creating application directory..."
    mkdir -p "$APP_DIR"
    log_success "Directory created: $APP_DIR"

    # Step 6: Clone Repository
    log_info "Step 6/9: Cloning repository..."
    
    if [ -d "$APP_DIR/.git" ]; then
        log_warning "Repository already exists, pulling updates..."
        cd "$APP_DIR"
        git fetch origin
        git checkout "$BRANCH"
        git pull origin "$BRANCH"
    else
        git clone -b "$BRANCH" "$REPO_URL" "$APP_DIR"
    fi
    
    log_success "Repository cloned/updated"

    # Step 7: Setup Environment
    log_info "Step 7/9: Setting up environment..."
    cd "$APP_DIR"
    
    if [ ! -f .env ]; then
        if [ -f .env.docker.example ]; then
            cp .env.docker.example .env
            log_success ".env file created from template"
            
            # Prompt for secure values
            log_warning "Please update .env with your configuration:"
            log_warning "  1. Database password: DB_PASSWORD"
            log_warning "  2. Redis password: REDIS_PASSWORD (if needed)"
            log_warning "  3. Edit: nano .env"
            log_warning "  4. Then run: docker-compose up -d"
            read -p "Press Enter after updating .env..."
        else
            log_error ".env.docker.example not found"
        fi
    else
        log_warning ".env already exists, skipping template copy"
    fi

    # Verify .env permissions
    chmod 600 .env
    
    # Step 8: Create Application User (optional)
    log_info "Step 8/9: Setting up application user permissions..."
    
    if ! id "$APP_USER" &>/dev/null; then
        log_info "Creating user: $APP_USER"
        useradd -r -s /bin/bash -d /opt/request-system "$APP_USER"
    fi
    
    chown -R "$APP_USER:$APP_USER" "$APP_DIR" || true
    
    log_success "Application user configured"

    # Step 9: Start Services
    log_info "Step 9/9: Starting Docker services..."
    
    # Pull latest images
    docker-compose pull
    
    # Start services
    docker-compose up -d
    
    # Wait for services to start
    sleep 10
    
    log_success "Docker services started"

    # Final verification
    log_info ""
    log_info "=========================================="
    log_info "Deployment Complete! ✅"
    log_info "=========================================="
    
    # Get server IP
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    log_info "API Access Information:"
    log_info "  Base URL:    http://$SERVER_IP:$APP_PORT"
    log_info "  Swagger UI:  http://$SERVER_IP:$APP_PORT/docs"
    log_info "  ReDoc:       http://$SERVER_IP:$APP_PORT/redoc"
    log_info "  Health:      http://$SERVER_IP:$APP_PORT/health"
    log_info ""
    
    log_info "Useful Commands:"
    log_info "  View logs:     docker-compose logs -f app"
    log_info "  Check status:  docker-compose ps"
    log_info "  Stop services: docker-compose down"
    log_info "  Restart:       docker-compose restart"
    log_info ""
    
    log_info "Next Steps:"
    log_info "  1. Edit .env with production settings"
    log_info "  2. Configure domain and SSL certificate (optional)"
    log_info "  3. Setup Nginx reverse proxy (optional)"
    log_info "  4. Configure monitoring and backups"
    log_info ""
    
    # Verify deployment
    log_info "Verifying deployment..."
    if curl -s http://localhost:$APP_PORT/health | jq . > /dev/null 2>&1; then
        log_success "Health check passed! Application is running."
    else
        log_warning "Health check failed. Check logs with: docker-compose logs app"
    fi
    
    log_info "For more information, see: docs/DEPLOYMENT.md"
}

# Run main function
main "$@"
