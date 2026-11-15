# Remote Deployment Setup Guide

**Table of Contents**
1. [Prerequisites](#prerequisites)
2. [SSH Setup](#ssh-setup)
3. [Automated Deployment](#automated-deployment)
4. [Manual Deployment](#manual-deployment)
5. [Code Updates](#code-updates)
6. [Nginx Reverse Proxy](#nginx-reverse-proxy)
7. [SSL/HTTPS Setup](#ssltls-with-lets-encrypt)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **VPS Server:** Ubuntu 20.04+, Debian 11+, CentOS 8+
- **Resources:** Minimum 2GB RAM, 20GB storage, 1 vCPU
- **Network:** SSH access (port 22 by default)
- **Domain:** Optional (for production with HTTPS)

### Required on Local Machine
- Git installed
- SSH client available
- Bash shell
- curl or wget

### Required on VPS Server (auto-installed by script)
- Docker
- Docker Compose
- PostgreSQL (in container)
- Redis (in container)
- Nginx (optional, for reverse proxy)

---

## SSH Setup

### Step 1: Generate SSH Keys (Local Machine)

```bash
# Generate SSH keys for deployment
bash scripts/setup-ssh-keys.sh

# Follow the prompts:
# - Generate new RSA 4096-bit key
# - Set optional passphrase
# - Configure SSH config file
```

**Output:**
```
Private key:  ~/.ssh/id_rsa_request_system
Public key:   ~/.ssh/id_rsa_request_system.pub
```

### Step 2: Add Public Key to VPS (Manual Method)

```bash
# On VPS server:
ssh ubuntu@your-vps-ip

# Create .ssh directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add public key from your local machine
echo "PASTE_YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Exit VPS
exit
```

### Step 3: Test SSH Connection

```bash
# Test connection
ssh -i ~/.ssh/id_rsa_request_system ubuntu@your-vps-ip

# If SSH config was created:
ssh request-system-vps
```

### Step 4: Disable Password Authentication (Optional but Recommended)

On VPS server:
```bash
sudo nano /etc/ssh/sshd_config

# Find and change these lines:
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin no

# Save and restart SSH
sudo systemctl restart sshd
```

---

## Automated Deployment

### One-Command Deployment (Recommended)

**From your local machine:**

```bash
bash scripts/remote-deploy.sh 192.168.1.100 ubuntu 22
```

**Parameters:**
- `192.168.1.100` - Your VPS IP address
- `ubuntu` - SSH username (default)
- `22` - SSH port (optional, default 22)

**Process (fully automated):**
1. ✓ Tests SSH connectivity
2. ✓ Updates system packages
3. ✓ Installs Docker
4. ✓ Installs Docker Compose
5. ✓ Clones repository
6. ✓ Creates environment file
7. ✓ Starts services
8. ✓ Verifies health checks

**Time:** 5-10 minutes  
**Output:**
```
✓ SSH connection established
✓ System updated
✓ Docker installed
✓ Docker Compose installed
✓ Repository cloned
✓ Environment file created
✓ Services started
✓ Health check passed

Access your application at:
  • API: http://192.168.1.100:8000
  • Swagger: http://192.168.1.100:8000/docs
```

---

## Manual Deployment

### Step 1: SSH to Your VPS

```bash
ssh ubuntu@your-vps-ip
```

### Step 2: Update System

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

### Step 3: Install Docker

```bash
# Using official Docker installation script
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
rm get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Step 4: Install Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker-compose --version
```

### Step 5: Clone Repository

```bash
sudo mkdir -p /opt/request-system
sudo git clone -b theodore/develop https://github.com/Matveyka20/Project_request_system.git /opt/request-system
cd /opt/request-system
```

### Step 6: Configure Environment

```bash
# Copy example configuration
cp .env.docker.example .env

# Edit with your settings
sudo nano .env

# Key settings to change:
# - DB_PASSWORD: Strong password
# - REDIS_PASSWORD: Strong password
# - ALLOWED_HOSTS: Your domain/IP

# Set proper permissions
chmod 600 .env
```

### Step 7: Start Services

```bash
docker-compose up -d

# Wait for services to start
sleep 10

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
```

### Step 8: Verify Deployment

```bash
# Health check
curl http://localhost:8000/health | jq .

# Swagger UI
curl http://localhost:8000/docs

# Test API
curl http://localhost:8000/api/requests | jq .
```

---

## Code Updates

### Push Code Changes to VPS

```bash
bash scripts/push-to-server.sh 192.168.1.100 ubuntu 22
```

**Process:**
1. ✓ Tests SSH connectivity
2. ✓ Pulls latest code from git
3. ✓ Restarts app service
4. ✓ Verifies health check

**From VPS shell (manual alternative):**
```bash
cd /opt/request-system
git fetch origin
git checkout theodore/develop
git pull origin theodore/develop
docker-compose restart app
```

---

## Nginx Reverse Proxy

### Step 1: Install Nginx

```bash
sudo apt-get install -y nginx
```

### Step 2: Copy Configuration

```bash
# From your local machine:
scp -i ~/.ssh/id_rsa_request_system nginx/request-system.conf ubuntu@your-vps-ip:~/

# On VPS:
sudo cp ~/request-system.conf /etc/nginx/sites-available/request-system
sudo ln -s /etc/nginx/sites-available/request-system /etc/nginx/sites-enabled/
```

### Step 3: Update Domain in Configuration

```bash
sudo nano /etc/nginx/sites-available/request-system

# Change these lines:
server_name your-domain.com www.your-domain.com;
ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
```

### Step 4: Test Nginx Configuration

```bash
sudo nginx -t
# Output should be: nginx: configuration file test is successful
```

### Step 5: Start Nginx

```bash
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## SSL/TLS with Let's Encrypt

### Step 1: Install Certbot

```bash
sudo apt-get install -y certbot python3-certbot-nginx
```

### Step 2: Generate SSL Certificate

```bash
# Get certificate
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com

# Follow the prompts:
# - Enter your email
# - Agree to terms
# - Choose preferred authentication method
```

### Step 3: Update Nginx Configuration

The SSL paths in nginx/request-system.conf should match:
```
ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
```

### Step 4: Setup Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Setup cron job for auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Verify
sudo systemctl status certbot.timer
```

### Step 5: Test HTTPS

```bash
# HTTP to HTTPS redirect
curl -I http://your-domain.com
# Should see: 301 Moved Permanently to https://

# HTTPS access
curl -I https://your-domain.com
# Should see: 200 OK

# Swagger UI
https://your-domain.com/docs
```

---

## Monitoring

### View Logs

```bash
# Application logs
docker-compose logs -f app

# All services
docker-compose logs -f

# Nginx logs
sudo tail -f /var/log/nginx/request-system-access.log
```

### Health Monitoring

```bash
# Start continuous monitoring
bash scripts/monitor.sh

# Or with Makefile
make monitor
```

### Database Monitoring

```bash
# Connect to database
docker-compose exec db psql -U postgres -d requests_db

# Count requests
SELECT COUNT(*) as total_requests FROM requests;

# Exit
\q
```

### Systemd Service Status

```bash
# Check service status
sudo systemctl status request-system

# View service logs
sudo journalctl -u request-system -f

# Restart service
sudo systemctl restart request-system
```

---

## Troubleshooting

### SSH Connection Issues

**Problem:** "Permission denied (publickey)"

```bash
# Check SSH key permissions
chmod 600 ~/.ssh/id_rsa_request_system
chmod 644 ~/.ssh/id_rsa_request_system.pub

# Check VPS authorized_keys
ssh ubuntu@your-vps-ip 'ls -la ~/.ssh/authorized_keys'

# Verify key is added
ssh ubuntu@your-vps-ip 'cat ~/.ssh/authorized_keys | grep request-system'
```

### Docker Issues

**Problem:** "Docker daemon not running"

```bash
# Restart Docker
sudo systemctl restart docker
sudo systemctl enable docker

# Check status
sudo systemctl status docker
```

**Problem:** "Permission denied while trying to connect to Docker daemon"

```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Exit and reconnect SSH
exit
```

### Port Already in Use

**Problem:** "Address already in use"

```bash
# Find process using port
sudo lsof -i :8000
sudo netstat -tulpn | grep 8000

# Kill process
sudo kill -9 <PID>

# Or change port in .env
APP_PORT=8001
docker-compose restart
```

### Health Check Failures

**Problem:** "Health check endpoint not responding"

```bash
# Check if container is running
docker-compose ps

# View container logs
docker-compose logs app

# Restart container
docker-compose restart app

# Test health endpoint directly
curl http://localhost:8000/health
```

### Nginx Not Working

**Problem:** "502 Bad Gateway"

```bash
# Check Nginx status
sudo systemctl status nginx

# Test Nginx config
sudo nginx -t

# Check backend is running
docker-compose ps

# View Nginx error log
sudo tail -f /var/log/nginx/request-system-error.log
```

### Database Connection Issues

**Problem:** "Unable to connect to database"

```bash
# Check database service
docker-compose ps db

# Test database connection
docker-compose exec db psql -U postgres -c "SELECT 1"

# Check .env credentials
grep DB_ /opt/request-system/.env
```

### Out of Disk Space

**Problem:** "No space left on device"

```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune -a

# Clean up logs
docker-compose logs --tail=0 > /dev/null

# Remove old backups
ls -la /opt/request-system/backups/
rm /opt/request-system/backups/backup_*.sql.gz  # Keep recent ones
```

---

## Common Commands

### Using Makefile

```bash
# SSH to server and use make commands
ssh ubuntu@your-vps-ip
cd /opt/request-system

# Useful commands:
make ps              # Show service status
make logs            # View application logs
make health          # Check health endpoint
make backup          # Create database backup
make restart         # Restart services
make clean           # Clean up resources
```

### Manual Docker Commands

```bash
# Start/stop services
docker-compose up -d
docker-compose down
docker-compose restart

# View logs
docker-compose logs -f app

# Execute commands in container
docker-compose exec app bash
docker-compose exec db psql -U postgres

# Remove everything (WARNING!)
docker-compose down -v
```

---

## Security Best Practices

1. **SSH Key Management**
   - Keep private key secure (chmod 600)
   - Use key passphrase
   - Rotate keys regularly
   - Never share private key

2. **Environment Variables**
   - Never commit .env to Git
   - Use strong passwords (16+ characters)
   - Generate SECRET_KEY randomly
   - Rotate secrets periodically

3. **Firewall Rules**
   ```bash
   # Allow SSH
   sudo ufw allow 22/tcp
   
   # Allow HTTP/HTTPS
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   
   # Enable firewall
   sudo ufw enable
   ```

4. **SSL/HTTPS**
   - Always use HTTPS in production
   - Setup Let's Encrypt auto-renewal
   - Use strong TLS versions (1.2, 1.3)

5. **Regular Backups**
   ```bash
   # Daily automated backup
   make backup
   
   # Store backups securely
   # Encrypt sensitive backups
   # Test restore procedures
   ```

---

## Support & Resources

- **GitHub Issues:** https://github.com/Matveyka20/Project_request_system/issues
- **Docker Docs:** https://docs.docker.com
- **Nginx Docs:** https://nginx.org/en/docs/
- **Let's Encrypt:** https://letsencrypt.org
- **Certbot Docs:** https://certbot.eff.org

---

**Last Updated:** November 15, 2026  
**Version:** 1.0
