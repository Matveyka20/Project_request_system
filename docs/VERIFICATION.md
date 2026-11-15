# Remote Application Verification Guide

This guide provides comprehensive instructions for verifying that the Request System API is deployed correctly and all endpoints are functioning properly on a remote server (VPS, cloud, etc.).

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Verification Approaches](#verification-approaches)
3. [Manual Testing](#manual-testing)
4. [Automated Testing](#automated-testing)
5. [Troubleshooting](#troubleshooting)
6. [API Endpoints Reference](#api-endpoints-reference)

---

## Quick Start

### Option 1: Quick Verification (if already deployed)

```bash
# Verify local deployment
bash scripts/remote-verify.sh localhost 8000

# Verify remote deployment
bash scripts/remote-verify.sh 192.168.1.100 8000

# Verify with specific port
bash scripts/remote-verify.sh your-domain.com 8000
```

### Option 2: Full Deployment + Verification

```bash
# Deploy and verify everything in one command
bash scripts/full-deploy-and-verify.sh 192.168.1.100 ubuntu 22

# Or using Makefile
make deploy-and-verify
```

### Option 3: Python Integration Tests

```bash
# Run integration tests against local deployment
pytest tests/test_remote_integration.py -v

# Run against remote deployment
API_BASE_URL=http://192.168.1.100:8000 pytest tests/test_remote_integration.py -v

# Generate coverage report
pytest tests/test_remote_integration.py -v --cov --html=report.html
```

---

## Verification Approaches

### Remote Verification Script (scripts/remote-verify.sh)

Automated bash script that tests all API endpoints:

**Tests Performed:**
1. ✅ Health Check - Endpoint `/health`
2. ✅ Ready Check - Endpoint `/ready`
3. ✅ List Requests - GET `/api/requests`
4. ✅ Pagination - GET `/api/requests?limit=5&offset=0`
5. ✅ Filter by Status - GET `/api/requests?status=submitted`
6. ✅ Search - GET `/api/requests?search=IT`
7. ✅ Sorting - GET `/api/requests?sort_by=created_at&sort_order=desc`
8. ✅ Filter by Priority - GET `/api/requests?priority=3`
9. ✅ Create Request - POST `/api/requests`
10. ✅ Get Single Request - GET `/api/requests/{id}`
11. ✅ Update Request - PATCH `/api/requests/{id}`
12. ✅ Change Status - PUT `/api/requests/{id}/status`
13. ✅ Swagger UI - GET `/docs`
14. ✅ ReDoc - GET `/redoc`
15. ✅ OpenAPI Schema - GET `/openapi.json`

**Usage:**
```bash
bash scripts/remote-verify.sh <SERVER_IP> [PORT]
```

**Example:**
```bash
bash scripts/remote-verify.sh 192.168.1.100 8000
bash scripts/remote-verify.sh your-api.example.com 8000
bash scripts/remote-verify.sh localhost 8000
```

**Output:**
- Colored output (Green = ✅ Pass, Red = ❌ Fail)
- HTTP status codes for each test
- JSON response bodies (if jq is available)
- Summary with passed/failed counts
- Exit code 0 if all passed, 1 if any failed

### Full Deployment + Verification Script (scripts/full-deploy-and-verify.sh)

Automated deployment script that:

1. **SSH Connectivity Check** - Verifies server is reachable
2. **System Updates** - Updates apt packages
3. **Docker Installation** - Installs Docker and Docker Compose
4. **Repository Deployment** - Clones/pulls latest code
5. **Environment Setup** - Creates .env with generated secure passwords
6. **Docker Services** - Starts all containers
7. **Database Initialization** - Runs seed data loading
8. **Health Checks** - Waits for application to be ready
9. **Full Verification** - Runs all verification tests

**Usage:**
```bash
bash scripts/full-deploy-and-verify.sh <SERVER_IP> <SERVER_USER> [SSH_PORT]
```

**Example:**
```bash
bash scripts/full-deploy-and-verify.sh 192.168.1.100 ubuntu 22
bash scripts/full-deploy-and-verify.sh your-vps.com root 22
```

---

## Manual Testing

### 1. Health Check

```bash
# Check application health
curl http://192.168.1.100:8000/health | jq .

# Expected Response:
# {
#   "status": "healthy",
#   "uptime": "0:00:45",
#   "timestamp": "2024-11-15T19:31:21.026+05:00",
#   "version": "1.0.0",
#   "database": "connected",
#   "cache": "connected"
# }
```

### 2. API Documentation

Open in browser:
- **Swagger UI (Interactive):** http://192.168.1.100:8000/docs
- **ReDoc (Reference):** http://192.168.1.100:8000/redoc
- **OpenAPI Schema:** http://192.168.1.100:8000/openapi.json

### 3. List All Requests

```bash
curl http://192.168.1.100:8000/api/requests | jq .

# Or with limit
curl "http://192.168.1.100:8000/api/requests?limit=5&offset=0" | jq .
```

### 4. Create a New Request

```bash
curl -X POST http://192.168.1.100:8000/api/requests \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "category_id": 1,
    "title": "Test Request",
    "description": "This is a test request",
    "priority": 3
  }' | jq .
```

### 5. Filter Requests

```bash
# By Status
curl "http://192.168.1.100:8000/api/requests?status=submitted" | jq .

# By Priority
curl "http://192.168.1.100:8000/api/requests?priority=2" | jq .

# By Category
curl "http://192.168.1.100:8000/api/requests?category_id=1" | jq .

# By User
curl "http://192.168.1.100:8000/api/requests?user_id=1" | jq .
```

### 6. Search Requests

```bash
# Full text search
curl "http://192.168.1.100:8000/api/requests?search=test" | jq .

# Search in description only
curl "http://192.168.1.100:8000/api/requests?search_description=IT" | jq .
```

### 7. Sort Requests

```bash
# By creation date (descending)
curl "http://192.168.1.100:8000/api/requests?sort_by=created_at&sort_order=desc&limit=10" | jq .

# By priority (ascending)
curl "http://192.168.1.100:8000/api/requests?sort_by=priority&sort_order=asc" | jq .

# By status
curl "http://192.168.1.100:8000/api/requests?sort_by=status&sort_order=asc" | jq .
```

### 8. Pagination

```bash
# Using limit + offset
curl "http://192.168.1.100:8000/api/requests?limit=10&offset=0" | jq .
curl "http://192.168.1.100:8000/api/requests?limit=10&offset=10" | jq .

# Using limit + page
curl "http://192.168.1.100:8000/api/requests?limit=10&page=1" | jq .
curl "http://192.168.1.100:8000/api/requests?limit=10&page=2" | jq .
```

### 9. Get Single Request

```bash
# First, get a request ID from list
REQUEST_ID=$(curl -s "http://192.168.1.100:8000/api/requests?limit=1" | jq -r '.requests[0].id')

# Get single request
curl "http://192.168.1.100:8000/api/requests/$REQUEST_ID" | jq .
```

### 10. Update Request

```bash
curl -X PATCH http://192.168.1.100:8000/api/requests/$REQUEST_ID \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "description": "Updated description",
    "priority": 4
  }' | jq .
```

### 11. Change Request Status

```bash
curl -X PUT http://192.168.1.100:8000/api/requests/$REQUEST_ID/status \
  -H "Content-Type: application/json" \
  -d '{"status_name": "in_progress"}' | jq .
```

---

## Automated Testing

### Python Integration Tests

Full test suite with 50+ test cases covering:

**Test Categories:**

1. **Connectivity Tests** (5 tests)
   - Health endpoint
   - Ready endpoint
   - OpenAPI schema
   - Documentation pages

2. **CRUD Operations** (12 tests)
   - List requests
   - Pagination
   - Filtering (status, priority, category, user)
   - Search
   - Sorting
   - Create request
   - Get single request
   - Update request
   - Change status

3. **Data Integrity Tests** (3 tests)
   - Seed data verification
   - Response structure validation
   - ID validation

4. **Error Handling Tests** (4 tests)
   - Invalid request IDs
   - Invalid parameters
   - Missing required fields
   - Parameter bounds

5. **Performance Tests** (3 tests)
   - Health check response time (< 1s)
   - List endpoint response time (< 5s)
   - Concurrent requests handling

**Running Tests:**

```bash
# Basic run
pytest tests/test_remote_integration.py -v

# Against remote server
API_BASE_URL=http://192.168.1.100:8000 pytest tests/test_remote_integration.py -v

# Specific test class
pytest tests/test_remote_integration.py::TestRequestsCRUD -v

# With coverage report
pytest tests/test_remote_integration.py -v --cov=src --html=report.html

# With output capture disabled
pytest tests/test_remote_integration.py -v -s

# Stop on first failure
pytest tests/test_remote_integration.py -v -x

# Run with timeout
pytest tests/test_remote_integration.py -v --timeout=30
```

**Example Output:**

```
tests/test_remote_integration.py::TestRemoteAPIConnectivity::test_health_endpoint PASSED [ 6%]
tests/test_remote_integration.py::TestRemoteAPIConnectivity::test_ready_endpoint PASSED [ 12%]
tests/test_remote_integration.py::TestRemoteAPIConnectivity::test_openapi_schema PASSED [ 18%]
tests/test_remote_integration.py::TestRemoteAPIConnectivity::test_docs_page PASSED [ 25%]
tests/test_remote_integration.py::TestRemoteAPIConnectivity::test_redoc_page PASSED [ 31%]
tests/test_remote_integration.py::TestRequestsCRUD::test_list_requests PASSED [ 37%]
tests/test_remote_integration.py::TestRequestsCRUD::test_create_request PASSED [ 43%]
tests/test_remote_integration.py::TestRequestsCRUD::test_filter_by_status PASSED [ 50%]
...

============================== 27 passed in 3.42s ==============================
```

---

## Expected Results

### Health Check Response

```json
{
  "status": "healthy",
  "uptime": "0:01:30",
  "timestamp": "2024-11-15T19:31:21.026+05:00",
  "version": "1.0.0",
  "database": "connected",
  "cache": "connected"
}
```

### List Requests Response

```json
{
  "requests": [
    {
      "id": 1,
      "user_id": 1,
      "category_id": 1,
      "title": "IT Support Request",
      "description": "Cannot login to system",
      "priority": 2,
      "status": "submitted",
      "created_at": "2024-11-15T10:00:00",
      "updated_at": "2024-11-15T10:00:00"
    },
    ...
  ],
  "total_count": 20,
  "filtered_count": 20,
  "returned_count": 10,
  "limit": 10,
  "offset": 0,
  "has_next": true,
  "has_previous": false
}
```

### Create Request Response

```json
{
  "id": 21,
  "user_id": 1,
  "category_id": 1,
  "title": "New Test Request",
  "description": "Test request from verification",
  "priority": 2,
  "status": "draft",
  "created_at": "2024-11-15T19:31:21.026+05:00",
  "updated_at": "2024-11-15T19:31:21.026+05:00"
}
```

---

## Verification Checklist

Use this checklist to verify your deployment:

### Pre-Deployment
- [ ] VPS/Server is created and accessible
- [ ] SSH key configured
- [ ] Domain name registered (optional)
- [ ] Firewall allows ports 22 (SSH), 80 (HTTP), 443 (HTTPS), 8000 (API)

### Deployment
- [ ] Repository cloned successfully
- [ ] Docker and Docker Compose installed
- [ ] `.env` file created with secure passwords
- [ ] Database initialized with seed data
- [ ] All containers running without errors

### Health Checks
- [ ] Health endpoint `/health` returns 200 OK
- [ ] Ready endpoint `/ready` returns ready=true
- [ ] Database is connected
- [ ] Cache (Redis) is connected
- [ ] API responds within expected time

### API Functionality
- [ ] Health check endpoint works
- [ ] List requests endpoint works
- [ ] Create request endpoint works
- [ ] Update request endpoint works
- [ ] Delete request endpoint works
- [ ] Filtering works (by status, priority, category)
- [ ] Search works
- [ ] Sorting works
- [ ] Pagination works

### Documentation
- [ ] Swagger UI accessible at `/docs`
- [ ] ReDoc accessible at `/redoc`
- [ ] OpenAPI schema accessible at `/openapi.json`
- [ ] All endpoints documented

### Monitoring
- [ ] Logs are accessible
- [ ] No error messages in logs
- [ ] Performance is acceptable (response times < 1s for health, < 5s for list)
- [ ] Database backups configured

---

## Troubleshooting

### API Not Responding

```bash
# Check server connectivity
ping 192.168.1.100

# Check if port 8000 is open
curl http://192.168.1.100:8000/health -v

# SSH into server and check containers
ssh user@192.168.1.100
docker-compose ps
docker-compose logs app
```

### Database Connection Failed

```bash
# Check database container
docker-compose ps db

# Check database logs
docker-compose logs db

# Test database connectivity
docker-compose exec db psql -U postgres -c "SELECT 1"
```

### Seed Data Not Loaded

```bash
# Reload seed data
docker-compose exec app python -m request_system.scripts.load_seed_data

# Verify data is loaded
docker-compose exec db psql -U postgres -d requests_db -c "SELECT COUNT(*) FROM requests"
```

### Performance Issues

```bash
# Check system resources
ssh user@192.168.1.100
top
df -h
free -h

# Check Docker container stats
docker stats

# Review application logs
docker-compose logs -f app --tail 50
```

### SSL/HTTPS Issues

```bash
# Check certificate
curl -v https://your-domain.com:443/health

# Renew Let's Encrypt certificate
sudo certbot renew

# Restart Nginx
sudo systemctl restart nginx
```

---

## API Endpoints Reference

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Application health status |
| GET | `/ready` | Application readiness |
| GET | `/docs` | Swagger UI documentation |
| GET | `/redoc` | ReDoc documentation |
| GET | `/openapi.json` | OpenAPI schema |

### Requests CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/requests` | List all requests |
| GET | `/api/requests/{id}` | Get single request |
| POST | `/api/requests` | Create new request |
| PATCH | `/api/requests/{id}` | Update request |
| PUT | `/api/requests/{id}/status` | Change request status |
| DELETE | `/api/requests/{id}` | Delete request |

### Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `user_id` | int | Filter by user | `?user_id=1` |
| `category_id` | int | Filter by category | `?category_id=1` |
| `status` | string | Filter by status | `?status=submitted` |
| `priority` | int | Filter by priority | `?priority=3` |
| `search` | string | Full-text search | `?search=test` |
| `search_description` | string | Search description | `?search_description=IT` |
| `sort_by` | string | Sort field | `?sort_by=created_at` |
| `sort_order` | string | Sort order (asc/desc) | `?sort_order=desc` |
| `limit` | int | Items per page | `?limit=10` |
| `offset` | int | Pagination offset | `?offset=0` |
| `page` | int | Page number | `?page=1` |

---

## Next Steps

1. **Monitor Deployment**
   ```bash
   docker-compose logs -f app
   ```

2. **Setup SSL/HTTPS**
   ```bash
   sudo certbot certonly --nginx -d your-domain.com
   ```

3. **Configure Monitoring**
   - Setup alerts for health check failures
   - Monitor response times
   - Track database performance

4. **Backup Strategy**
   ```bash
   docker-compose exec db pg_dump -U postgres requests_db > backup.sql
   ```

5. **Scaling**
   - Add load balancer (Nginx)
   - Multiple API instances
   - Database replication

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review application logs: `docker-compose logs app`
3. Open an issue on GitHub
4. Contact development team

**Last Updated:** November 15, 2024  
**Version:** 1.0
