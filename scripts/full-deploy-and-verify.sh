#!/bin/bash

# Full Deployment and Verification Script
# Deploys the application to a VPS and runs complete verification tests

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SERVER_IP=${1:-}
SERVER_USER=${2:-}
SSH_PORT=${3:-22}
REPO_URL="https://github.com/TheodorePrescott821/Karpov_Matvey_ISIP-308_RequestSystem.git"
REPO_BRANCH="develop"
APP_DIR="/opt/request-system"

# Validation
if [ -z "$SERVER_IP" ] || [ -z "$SERVER_USER" ]; then
    echo -e "${RED}Usage: $0 <SERVER_IP> <SERVER_USER> [SSH_PORT]${NC}"
    echo "Example: $0 192.168.1.100 ubuntu 22"
    exit 1
fi

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Full Deployment and Verification${NC}"
echo -e "${YELLOW}========================================${NC}"
echo "Server: $SERVER_USER@$SERVER_IP:$SSH_PORT"
echo "Repository: $REPO_URL"
echo "Branch: $REPO_BRANCH"
echo "App Directory: $APP_DIR"
echo ""

# Step 1: SSH connectivity check
echo -e "${BLUE}Step 1: Checking SSH connectivity...${NC}"
if ! ssh -p $SSH_PORT -o ConnectTimeout=5 "$SERVER_USER@$SERVER_IP" "echo 'SSH OK'" &>/dev/null; then
    echo -e "${RED}❌ Cannot connect to server via SSH${NC}"
    exit 1
fi
echo -e "${GREEN}✅ SSH connectivity established${NC}"

# Step 2: Deploy application
echo -e "\n${BLUE}Step 2: Deploying application...${NC}"
ssh -p $SSH_PORT "$SERVER_USER@$SERVER_IP" << 'EOF'
    set -e
    
    echo "Updating system..."
    sudo apt-get update -qq
    
    echo "Installing Docker dependencies..."
    sudo apt-get install -y -qq apt-transport-https ca-certificates curl software-properties-common jq
    
    # Check if Docker is already installed
    if ! command -v docker &> /dev/null; then
        echo "Installing Docker..."
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
        sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" -y
        sudo apt-get update -qq
        sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io
        
        # Add user to docker group
        sudo usermod -aG docker $USER
        
        echo "Docker installed successfully"
    else
        echo "Docker already installed"
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        echo "Installing Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    else
        echo "Docker Compose already installed"
    fi
EOF

# Step 3: Clone/pull repository
echo -e "\n${BLUE}Step 3: Cloning/updating repository...${NC}"
ssh -p $SSH_PORT "$SERVER_USER@$SERVER_IP" << EOF
    set -e
    
    if [ -d "$APP_DIR" ]; then
        echo "Updating existing repository..."
        cd $APP_DIR
        git fetch origin
        git checkout $REPO_BRANCH
        git pull origin $REPO_BRANCH
    else
        echo "Cloning repository..."
        sudo mkdir -p $APP_DIR
        sudo git clone -b $REPO_BRANCH $REPO_URL $APP_DIR
        sudo chown -R $USER:$USER $APP_DIR
    fi
    
    echo "Repository ready at $APP_DIR"
EOF

# Step 4: Setup environment
echo -e "\n${BLUE}Step 4: Setting up environment...${NC}"
ssh -p $SSH_PORT "$SERVER_USER@$SERVER_IP" << EOF
    set -e
    
    cd $APP_DIR
    
    if [ ! -f .env ]; then
        echo "Creating .env from .env.docker.example..."
        cp .env.docker.example .env
        
        # Generate secure password
        DB_PASS=\$(openssl rand -base64 12)
        REDIS_PASS=\$(openssl rand -base64 12)
        SECRET_KEY=\$(openssl rand -base64 32)
        
        # Update .env with generated values
        sed -i "s|DB_PASSWORD=.*|DB_PASSWORD=\$DB_PASS|" .env
        sed -i "s|REDIS_PASSWORD=.*|REDIS_PASSWORD=\$REDIS_PASS|" .env
        sed -i "s|SECRET_KEY=.*|SECRET_KEY=\$SECRET_KEY|" .env
        sed -i "s|APP_ENV=.*|APP_ENV=production|" .env
        sed -i "s|APP_DEBUG=.*|APP_DEBUG=false|" .env
        
        echo "Environment configured"
    else
        echo ".env already exists"
    fi
EOF

# Step 5: Start Docker services
echo -e "\n${BLUE}Step 5: Starting Docker services...${NC}"
ssh -p $SSH_PORT "$SERVER_USER@$SERVER_IP" << EOF
    set -e
    
    cd $APP_DIR
    
    echo "Pulling images..."
    docker-compose pull
    
    echo "Starting services..."
    docker-compose up -d
    
    echo "Waiting for services to start..."
    sleep 10
    
    echo "Service status:"
    docker-compose ps
EOF

# Step 6: Initialize database
echo -e "\n${BLUE}Step 6: Initializing database...${NC}"
ssh -p $SSH_PORT "$SERVER_USER@$SERVER_IP" << EOF
    set -e
    
    cd $APP_DIR
    
    echo "Running database initialization..."
    docker-compose exec -T app python -m request_system.scripts.load_seed_data
    
    echo "Database initialized"
EOF

# Step 7: Health check
echo -e "\n${BLUE}Step 7: Checking application health...${NC}"
API_PORT=8000
for i in {1..30}; do
    if ssh -p $SSH_PORT "$SERVER_USER@$SERVER_IP" "curl -s http://localhost:$API_PORT/health" &>/dev/null; then
        echo -e "${GREEN}✅ Application is healthy${NC}"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Application did not become healthy${NC}"
        exit 1
    fi
    
    echo "Waiting for application... ($i/30)"
    sleep 2
done

# Step 8: Run remote verification
echo -e "\n${BLUE}Step 8: Running verification tests...${NC}"

# Get server's IP from inside the container
SERVER_REAL_IP=$SERVER_IP

# Download verification script and run it
ssh -p $SSH_PORT "$SERVER_USER@$SERVER_IP" << EOF
    set -e
    
    cd $APP_DIR
    
    # Make script executable
    chmod +x scripts/remote-verify.sh
    
    # Run verification
    bash scripts/remote-verify.sh localhost 8000
EOF

# Final report
echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}Deployment Complete${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "${GREEN}✅ Application successfully deployed and verified${NC}"
echo ""
echo "Access your application:"
echo -e "  API Documentation: ${BLUE}http://$SERVER_IP:8000/docs${NC}"
echo -e "  ReDoc: ${BLUE}http://$SERVER_IP:8000/redoc${NC}"
echo -e "  API Base URL: ${BLUE}http://$SERVER_IP:8000/api${NC}"
echo ""
echo "SSH into server:"
echo -e "  ${BLUE}ssh -p $SSH_PORT $SERVER_USER@$SERVER_IP${NC}"
echo ""
echo "View logs:"
echo -e "  ${BLUE}ssh -p $SSH_PORT $SERVER_USER@$SERVER_IP 'cd $APP_DIR && docker-compose logs -f app'${NC}"
echo ""
