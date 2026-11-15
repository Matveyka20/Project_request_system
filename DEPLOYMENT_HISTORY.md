# Deployment History

## Current Production Deployment

| Property | Value |
|----------|-------|
| **Application Address** | [To be filled] |
| **Deploy Date** | [To be filled] |
| **Environment** | production / staging |
| **VPS Provider** | DigitalOcean / Hetzner / Linode / Other |
| **Server Location** | Region/City |
| **OS** | Ubuntu 20.04 LTS / Debian 11 / CentOS 8 |
| **Docker Version** | [To be filled] |
| **API Version** | v1.2.0 (Phase 5) |
| **Database** | PostgreSQL 15 / SQLite |
| **Cache** | Redis 7 |
| **Status** | ✅ Active / ⚠️ Maintenance / ❌ Down |

## Deployment Details

### Latest Deployment
- **Application URL**: http://[IP/domain]:8000
- **Swagger UI**: http://[IP/domain]:8000/docs
- **ReDoc**: http://[IP/domain]:8000/redoc
- **Health Check**: http://[IP/domain]:8000/health
- **Admin Panel**: http://[IP/domain]:5050 (pgAdmin, if enabled)

### Deployment Method
- [ ] Automated script (scripts/full-deploy-and-verify.sh)
- [ ] Manual deployment (step-by-step)
- [ ] GitHub Actions CI/CD
- [ ] Other: ___________

### Services Running
- ✅ FastAPI Application (port 8000)
- ✅ PostgreSQL Database (port 5432, internal)
- ✅ Redis Cache (port 6379, internal)
- ⚠️ pgAdmin (port 5050, development only)
- ⚠️ Nginx Reverse Proxy (if configured)

### Database Status
- Initial migration date: [To be filled]
- Seed data loaded: [To be filled]
- Tables initialized: Users, Categories, Statuses, Requests
- Total records: [To be filled]

### SSL/HTTPS
- Certificate: [Self-signed / Let's Encrypt / None]
- Domain: [To be filled]
- Expiry Date: [To be filled]

## Previous Deployments

(None yet - this is the first deployment)

## Quick Access

```bash
# SSH into server
ssh -i [path/to/key] ubuntu@[SERVER_IP]

# View application logs
docker-compose logs -f app

# Check health
curl http://[SERVER_IP]:8000/health

# Restart services
docker-compose restart
```

---

**Last Updated:** November 15, 2026
