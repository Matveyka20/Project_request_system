# Deployment Checklist

Complete this checklist before, during, and after deployment to production.

---

## Pre-Deployment Planning

- [ ] VPS server selected and created
- [ ] IP address and SSH credentials documented
- [ ] Domain name registered (if using HTTPS)
- [ ] Email address ready for Let's Encrypt
- [ ] Backup plan documented
- [ ] Rollback plan documented
- [ ] Team notified of deployment schedule
- [ ] Maintenance window scheduled if needed

---

## SSH & Access Setup

- [ ] SSH key pair generated locally
- [ ] Public key added to VPS authorized_keys
- [ ] SSH connection tested successfully
- [ ] SSH config file updated (optional)
- [ ] Firewall configured to allow port 22
- [ ] Password authentication disabled (optional)
- [ ] SSH key stored securely
- [ ] Backup of SSH key created

---

## VPS Server Preparation

- [ ] VPS created with minimum 2GB RAM
- [ ] Operating system is Ubuntu 20.04+ or equivalent
- [ ] System fully updated: `sudo apt-get update && upgrade`
- [ ] Required ports open: 22 (SSH), 80 (HTTP), 443 (HTTPS)
- [ ] Firewall configured and enabled
- [ ] Hostname set appropriately
- [ ] Time zone configured correctly
- [ ] Swap space configured (if needed)

---

## Automated Deployment Execution

### Option A: Using Deployment Script

- [ ] Local machine has Git and SSH key
- [ ] Repository cloned locally
- [ ] `scripts/remote-deploy.sh` is executable
- [ ] Server IP, username, port noted
- [ ] Deployment script executed:
  ```bash
  bash scripts/remote-deploy.sh <IP> <USER> <PORT>
  ```
- [ ] Script completed without errors
- [ ] Deployment log saved for reference
- [ ] Services showing as running:
  ```bash
  docker-compose ps
  # All containers should show "Up"
  ```

### Option B: Manual Deployment

- [ ] SSH session active to VPS
- [ ] Docker installed successfully
- [ ] Docker Compose installed successfully
- [ ] Repository cloned to `/opt/request-system`
- [ ] Repository on correct branch: `theodore/develop`
- [ ] Environment file created from template
- [ ] Database and Redis passwords changed
- [ ] SECRET_KEY generated and set
- [ ] ALLOWED_HOSTS updated with server IP/domain
- [ ] Services started:
  ```bash
  docker-compose up -d
  ```
- [ ] Services running:
  ```bash
  docker-compose ps
  # All containers should show "Up"
  ```

---

## Service Verification

- [ ] Application container is running
- [ ] PostgreSQL database container is running
- [ ] Redis cache container is running
- [ ] All containers in "healthy" state
- [ ] No error messages in container logs
- [ ] Application listening on port 8000:
  ```bash
  docker-compose exec app netstat -tulpn | grep 8000
  ```
- [ ] Database accessible:
  ```bash
  docker-compose exec db psql -U postgres -c "SELECT 1"
  ```

---

## Health Checks

- [ ] `/health` endpoint responds with 200:
  ```bash
  curl http://localhost:8000/health | jq .
  # Status should be "healthy"
  ```
- [ ] `/ready` endpoint responds with 200:
  ```bash
  curl http://localhost:8000/ready | jq .
  # ready should be true
  ```
- [ ] API endpoint responds:
  ```bash
  curl http://localhost:8000/api/requests | jq .
  # Should return JSON response
  ```
- [ ] Swagger UI accessible:
  ```bash
  curl http://localhost:8000/docs
  # Should return HTML
  ```
- [ ] All health checks pass from external machine

---

## Database Setup

- [ ] Database migrated (if applicable):
  ```bash
  docker-compose exec app alembic upgrade head
  ```
- [ ] Initial data loaded (if applicable)
- [ ] Database user permissions correct
- [ ] PostgreSQL backup configured
- [ ] Database backup created before going live
- [ ] Backup can be restored successfully
- [ ] Replication setup (if needed)

---

## Nginx Reverse Proxy Setup

- [ ] Nginx installed on VPS
- [ ] Configuration file copied:
  ```bash
  sudo cp nginx/request-system.conf /etc/nginx/sites-available/
  ```
- [ ] Symbolic link created:
  ```bash
  sudo ln -s /etc/nginx/sites-available/request-system /etc/nginx/sites-enabled/
  ```
- [ ] Domain name updated in config
- [ ] Configuration tested:
  ```bash
  sudo nginx -t
  ```
- [ ] Nginx restarted:
  ```bash
  sudo systemctl restart nginx
  ```
- [ ] Nginx status verified:
  ```bash
  sudo systemctl status nginx
  ```
- [ ] HTTP requests forwarded correctly:
  ```bash
  curl -I http://your-vps-ip/health
  ```

---

## SSL/HTTPS Setup

- [ ] Certbot installed:
  ```bash
  sudo apt-get install certbot python3-certbot-nginx
  ```
- [ ] SSL certificate obtained:
  ```bash
  sudo certbot certonly --nginx -d your-domain.com
  ```
- [ ] Nginx config updated with certificate paths
- [ ] SSL configuration tested:
  ```bash
  curl -I https://your-domain.com/
  ```
- [ ] HTTP to HTTPS redirect working
- [ ] Auto-renewal configured:
  ```bash
  sudo systemctl enable certbot.timer
  ```
- [ ] Auto-renewal tested:
  ```bash
  sudo certbot renew --dry-run
  ```
- [ ] SSL certificate valid for 90+ days
- [ ] Certificate renewal reminder set

---

## Monitoring & Logging

- [ ] Application logs accessible:
  ```bash
  docker-compose logs -f app
  ```
- [ ] Nginx logs accessible:
  ```bash
  sudo tail -f /var/log/nginx/request-system-access.log
  ```
- [ ] Health monitoring script configured:
  ```bash
  bash scripts/monitor.sh
  ```
- [ ] Monitoring running in background
- [ ] Log rotation configured
- [ ] Disk space monitoring setup
- [ ] Error alerting configured (if available)

---

## Backup & Disaster Recovery

- [ ] Backup script configured:
  ```bash
  make backup
  # or bash scripts/monitor.sh for automation
  ```
- [ ] Daily automatic backups scheduled
- [ ] Backup directory created and secured
- [ ] Backup retention policy set (e.g., 30 days)
- [ ] Backup tested and can be restored:
  ```bash
  # Test restore process
  ```
- [ ] Database dump tested
- [ ] Docker volume backups configured
- [ ] Off-site backup location identified
- [ ] Disaster recovery plan documented

---

## Security Hardening

- [ ] SSH key authentication working
- [ ] Password authentication disabled
- [ ] Root login disabled
- [ ] Firewall rules configured:
  ```bash
  sudo ufw allow 22/tcp
  sudo ufw allow 80/tcp
  sudo ufw allow 443/tcp
  sudo ufw enable
  ```
- [ ] Environment variables secured (.env not in Git)
- [ ] Database passwords strong (16+ characters)
- [ ] Redis passwords strong (16+ characters)
- [ ] SECRET_KEY randomly generated
- [ ] CORS origins restricted to your domain
- [ ] Rate limiting enabled
- [ ] Security headers configured in Nginx
- [ ] File permissions correct (600 for .env)
- [ ] Container runs as non-root user

---

## Performance Testing

- [ ] Page load times acceptable
- [ ] API response times acceptable
- [ ] Database query performance acceptable
- [ ] Cache working (Redis)
- [ ] No N+1 queries detected
- [ ] Resource usage acceptable:
  ```bash
  docker stats
  ```
- [ ] CPU usage within limits
- [ ] Memory usage within limits
- [ ] Disk I/O acceptable
- [ ] Network latency acceptable

---

## Integration Testing

- [ ] Create request (POST /api/requests)
- [ ] Read request (GET /api/requests/{id})
- [ ] Update request (PATCH /api/requests/{id})
- [ ] Change status (PUT /api/requests/{id}/status)
- [ ] List requests (GET /api/requests)
- [ ] Search functionality working
- [ ] Filtering working
- [ ] Sorting working
- [ ] Pagination working
- [ ] Error responses correct (404, 422, 500)

---

## External Verification

- [ ] API accessible from different network
- [ ] Swagger UI accessible from external machine
- [ ] Health check passes from external IP
- [ ] SSL certificate valid and trusted
- [ ] Domain resolves correctly
- [ ] Reverse proxy forwarding working
- [ ] Rate limiting working properly
- [ ] CORS headers correct

---

## Documentation & Knowledge Transfer

- [ ] Deployment documented in README
- [ ] Server access details recorded securely
- [ ] Deployment steps documented
- [ ] Password change procedures documented
- [ ] Backup/restore procedures documented
- [ ] Monitoring setup documented
- [ ] Team trained on maintenance procedures
- [ ] On-call support process defined
- [ ] Escalation procedures documented

---

## Post-Deployment Monitoring (24 hours)

- [ ] No unusual error patterns
- [ ] Disk space not filling up
- [ ] Memory usage stable
- [ ] CPU usage normal
- [ ] Database performing well
- [ ] Backups completing successfully
- [ ] No security incidents
- [ ] Users can access application
- [ ] API response times stable
- [ ] Database connection pool healthy

---

## Post-Deployment Follow-up (1 week)

- [ ] Application stable in production
- [ ] No critical bugs reported
- [ ] Performance metrics acceptable
- [ ] User feedback positive
- [ ] Cost within budget
- [ ] Scaling plan reviewed (if needed)
- [ ] Upgrade plan documented
- [ ] Team feedback collected
- [ ] Deployment retrospective scheduled
- [ ] Lessons learned documented

---

## Rollback Procedure (if needed)

- [ ] Previous version backup available
- [ ] Rollback procedure tested
- [ ] Communication plan for rollback
- [ ] Customer notification prepared
- [ ] Database rollback procedure tested
- [ ] Rollback time estimate documented

---

## Sign-Off

- [ ] **Deployment Lead:** _________________ Date: _______
- [ ] **QA Tester:** _________________ Date: _______
- [ ] **DevOps/Admin:** _________________ Date: _______
- [ ] **Project Manager:** _________________ Date: _______

---

## Notes

```
Use this space for any additional notes or issues encountered:

[Your notes here]
```

---

**Deployment Date:** _____________  
**Deployed Version:** _____________  
**Deployment Duration:** _____________  
**Issues Encountered:** _____________  

---

*Print this checklist and keep it for compliance and audit purposes.*
