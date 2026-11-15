# VPS Deployment Guide for Request System API

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start (Automated)](#quick-start-automated)
3. [Manual Deployment](#manual-deployment)
4. [Configuration](#configuration)
5. [Access Services](#access-services)
6. [Reverse Proxy Setup](#reverse-proxy-setup)
7. [SSL Certificate](#ssl-certificate)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)
10. [Recommended VPS Providers](#recommended-vps-providers)

---

## Prerequisites

### System Requirements
- **OS:** Ubuntu 20.04+ / Debian 11+ / CentOS 8+ / Rocky Linux 8+
- **RAM:** Minimum 2GB (4GB recommended for production)
- **Storage:** 20GB minimum (SSD recommended)
- **CPU:** 1 vCPU minimum (2 vCPU recommended)

### Access Requirements
- SSH access to the server
- `sudo` privileges (or root access)
- Git installed (optional, for manual clone)

### Additional (Optional)
- Domain name (for SSL and reverse proxy)
- Email address (for Let's Encrypt SSL)

---

## Quick Start (Automated)

### Option 1: One-Command Deployment

```bash
# SSH into your VPS
ssh -i /path/to/key.pem ubuntu@your-vps-ip

# Run deployment script
curl -sSL https://raw.githubusercontent.com/Matveyka20/Project_request_system/theodore/develop/scripts/deploy.sh | sudo bash
```

The script will:
1. Update system packages
2. Install Docker and Docker Compose
3. Clone the repository
4. Setup application directory
5. Start all services

### Option 2: One-Step (Manual, If Script Fails)

```bash
# SSH to server
ssh ubuntu@your-vps-ip

# Download and run script locally
wget https://raw.githubusercontent.com/Matveyka20/Project_request_system/theodore/develop/scripts/deploy.sh
sudo bash deploy.sh
```

---

## Manual Deployment

### Step 1: SSH into Server

```bash
ssh -i /path/to/key.pem ubuntu@your-vps-ip
```

Or if using password:
```bash
ssh ubuntu@your-vps-ip
```

### Step 2: Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 3: Install Docker

```bash
# Install prerequisites
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### Step 4: Install Docker Compose

```bash
# Get latest version
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d'"' -f4)

# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### Step 5: Clone Repository

```bash
# Create application directory
sudo mkdir -p /opt/request-system
cd /opt/request-system

# Clone repository
sudo git clone -b theodore/develop https://github.com/Matveyka20/Project_request_system.git .
```

### Step 6: Configure Environment

```bash
# Copy environment template
sudo cp .env.docker.example .env

# Edit with your settings (database password, etc.)
sudo nano .env

# Set proper permissions
sudo chmod 600 .env
```

**Important environment variables to configure:**
```bash
APP_ENV=production
APP_DEBUG=false
APP_PORT=8000

# Database
DB_USER=postgres
DB_PASSWORD=YOUR_SECURE_PASSWORD_HERE
DB_NAME=requests_db

# Redis (optional)
REDIS_PASSWORD=YOUR_REDIS_PASSWORD_HERE

# Logging
LOG_LEVEL=INFO
```

### Step 7: Start Services

```bash
# Start all services
sudo docker-compose up -d

# Wait for initialization
sleep 15

# Check status
sudo docker-compose ps
```

### Step 8: Verify Deployment

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected output:
# {
#   "status": "healthy",
#   "version": "1.1.0",
#   "timestamp": "2026-11-15T19:12:15Z",
#   "uptime_seconds": 15.5,
#   "database": "ok",
#   "cache": "ok",
#   "environment": "production",
#   "python_version": "3.11.0"
# }

# Check Swagger UI
curl -I http://localhost:8000/docs
# Should return: HTTP/1.1 200 OK
```

---

## Configuration

### Environment Variables

Create or edit `.env` file in `/opt/request-system/`:

```bash
# Application Environment
APP_ENV=production           # development, staging, production
APP_DEBUG=false              # Never true in production!
APP_PORT=8000                # Internal container port
APP_HOST=0.0.0.0             # Bind address
APP_WORKERS=4                # Uvicorn workers
APP_NAME="Request System"    # Application name

# Database
DATABASE_URL=postgresql://postgres:PASSWORD@db:5432/requests_db
DATABASE_POOL_SIZE=10        # Connection pool size
DATABASE_ECHO_SQL=false      # Log SQL queries

# Redis Cache (optional)
REDIS_URL=redis://:PASSWORD@cache:6379/0

# API Configuration
API_PREFIX=/api              # API route prefix
API_TITLE=Request System API
API_VERSION=1.1.0
API_CORS_ORIGINS=*           # CORS allowed origins

# Logging
LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Database Password Generation

```bash
# Generate secure password
openssl rand -base64 32

# Or using Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Access Services

### API Endpoints

After deployment, services are available at:

| Service | URL | Purpose |
|---------|-----|---------|
| **API** | http://your-vps-ip:8000 | REST API base URL |
| **Swagger UI** | http://your-vps-ip:8000/docs | Interactive API documentation |
| **ReDoc** | http://your-vps-ip:8000/redoc | Alternative API documentation |
| **Health Check** | http://your-vps-ip:8000/health | Application health status |
| **Readiness Check** | http://your-vps-ip:8000/ready | Service readiness |
| **pgAdmin** | http://your-vps-ip:5050 | Database management (dev only) |

### Example API Calls

```bash
# Get all requests
curl http://your-vps-ip:8000/api/requests

# Create a new request
curl -X POST http://your-vps-ip:8000/api/requests \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "description": "Test request",
    "account_name": "Test Account",
    "category_id": 1,
    "priority": "Высокий"
  }'

# Search requests
curl "http://your-vps-ip:8000/api/requests?search=laptop&limit=10"

# Filter by status
curl "http://your-vps-ip:8000/api/requests?status=В%20работе"
```

---

## Reverse Proxy Setup

### Nginx Configuration (Recommended)

Install Nginx:
```bash
sudo apt-get install -y nginx
```

Create configuration:
```bash
sudo tee /etc/nginx/sites-available/request-system > /dev/null <<'EOF'
upstream request_system {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://request_system;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Static files cache
    location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF
```

Enable configuration:
```bash
sudo ln -s /etc/nginx/sites-available/request-system /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

## SSL Certificate

### Let's Encrypt (Free, Automated)

Install Certbot:
```bash
sudo apt-get install -y certbot python3-certbot-nginx
```

Get certificate:
```bash
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com
```

Update Nginx configuration:
```bash
sudo tee /etc/nginx/sites-available/request-system > /dev/null <<'EOF'
upstream request_system {
    server localhost:8000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS configuration
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 10M;

    location / {
        proxy_pass http://request_system;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
EOF
```

Test and reload:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

Auto-renewal:
```bash
# Check renewal configuration
sudo certbot renew --dry-run

# Certbot sets up automatic renewal via systemd timer
sudo systemctl enable certbot.timer
```

---

## Monitoring & Maintenance

### View Application Logs

```bash
# Real-time logs
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app

# Show logs for specific time period
docker-compose logs --since 10m app
```

### Monitor Container Status

```bash
# Check all containers
docker-compose ps

# View container resource usage
docker stats

# Container details
docker inspect request-system-api
```

### Health Monitoring Script

```bash
# Run health monitor (checks every 60 seconds)
bash scripts/monitor.sh

# View health check history
tail -f health-monitor.log

# Stop monitoring
Ctrl+C
```

### Database Backup

```bash
# Backup database
docker-compose exec db pg_dump -U postgres requests_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Compress backup
gzip backup_*.sql

# List backups
ls -lh backup_*.sql*
```

### Database Restore

```bash
# Restore from backup
docker-compose exec -T db psql -U postgres requests_db < backup_20241115_191215.sql

# Or from compressed backup
gunzip backup_20241115_191215.sql.gz
docker-compose exec -T db psql -U postgres requests_db < backup_20241115_191215.sql
```

### Automated Backups (Cron)

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /opt/request-system && docker-compose exec -T db pg_dump -U postgres requests_db | gzip > backups/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz
```

### Restart Services

```bash
# Restart specific service
docker-compose restart app

# Restart all services
docker-compose restart

# Stop services
docker-compose down

# Start services
docker-compose up -d
```

### Update Application

```bash
# Pull latest code
cd /opt/request-system
git pull origin theodore/develop

# Rebuild image
docker-compose build app

# Restart with new image
docker-compose up -d app
```

---

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8000
sudo netstat -tulpn | grep 8000
sudo lsof -i :8000

# Find and kill process
sudo kill -9 <PID>

# Or use different port in .env
APP_PORT=9000
docker-compose restart
```

### Docker Permission Denied

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker

# Verify (no sudo needed)
docker ps
```

### Database Connection Refused

```bash
# Check database service
docker-compose ps db

# View database logs
docker-compose logs db

# Verify credentials in .env
cat .env | grep DB_

# Restart database
docker-compose restart db
```

### Health Check Failing

```bash
# Check if service is running
docker-compose ps

# View service logs
docker-compose logs app

# Test health endpoint
curl -v http://localhost:8000/health

# Check container resource usage
docker stats request-system-api
```

### Out of Disk Space

```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune

# Remove unused volumes
docker volume prune

# View disk space by Docker
docker system df
```

### Service Won't Start

```bash
# Check for errors
docker-compose logs app

# Try rebuilding
docker-compose build --no-cache app

# Restart
docker-compose up -d
```

### Nginx 502 Bad Gateway

```bash
# Check if app is running
curl http://localhost:8000/health

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Verify proxy configuration
sudo nginx -t
```

---

## Recommended VPS Providers

### Budget-Friendly

| Provider | Specs | Price | Link |
|----------|-------|-------|------|
| **Hetzner Cloud** | 2GB RAM, 40GB SSD, 1 vCPU | $2.99/mo | [hetzner.com](https://www.hetzner.com/cloud) |
| **Linode** | 2GB RAM, 50GB SSD, 1 vCPU | $5/mo | [linode.com](https://www.linode.com) |
| **DigitalOcean** | 2GB RAM, 50GB SSD, 1 vCPU | $5/mo | [digitalocean.com](https://www.digitalocean.com) |
| **Vultr** | 2GB RAM, 60GB SSD, 1 vCPU | $2.50/mo | [vultr.com](https://www.vultr.com) |

### Production-Grade

| Provider | Specs | Price | Link |
|----------|-------|-------|------|
| **AWS** | t3.small (2GB, 1 vCPU) | $15.46/mo | [aws.amazon.com](https://aws.amazon.com/ec2/) |
| **Google Cloud** | e2-small (2GB, 1 vCPU) | $10.34/mo | [cloud.google.com](https://cloud.google.com/compute) |
| **Azure** | B1s (1GB, 1 vCPU) | $7.59/mo | [azure.microsoft.com](https://azure.microsoft.com/vm) |

### Comparison

| Feature | Hetzner | Linode | DigitalOcean | Vultr | AWS |
|---------|---------|--------|--------------|-------|-----|
| **Price** | ★★★★★ | ★★★★ | ★★★★ | ★★★★★ | ★★ |
| **Performance** | ★★★★★ | ★★★★★ | ★★★★ | ★★★★ | ★★★★★ |
| **UI/UX** | ★★★★ | ★★★★ | ★★★★★ | ★★★ | ★★ |
| **Support** | ★★★★ | ★★★★★ | ★★★★★ | ★★★ | ★★★★★ |
| **Setup Ease** | ★★★★ | ★★★★★ | ★★★★★ | ★★★★ | ★★★ |

**Recommendation for beginners:** DigitalOcean or Linode (excellent documentation and support)

---

## Support & Documentation

- **Full API Documentation:** http://your-vps-ip:8000/docs
- **GitHub Repository:** https://github.com/Matveyka20/Project_request_system
- **Issues & Bug Reports:** https://github.com/Matveyka20/Project_request_system/issues
- **Docker Documentation:** https://docs.docker.com
- **Docker Compose:** https://docs.docker.com/compose

---

**Last Updated:** November 15, 2024  
**Version:** 1.0.0  
**Status:** Production Ready ✅
