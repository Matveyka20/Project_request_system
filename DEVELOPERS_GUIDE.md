# Developers Guide - Lab 8

## Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (for containerized development)
- Git
- Make (optional, but recommended)

### Local Development Setup

#### 1. Clone Repository
```bash
git clone https://github.com/your-org/request-system.git
cd request-system
```

#### 2. Create Virtual Environment
```bash
# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
# Install in editable mode with dev dependencies
python -m pip install -e ".[dev]"

# Or just install requirements
python -m pip install -r requirements.txt
```

#### 4. Run Local Server
```bash
# Direct execution
python -m uvicorn src.request_system.presentation.main:app --reload --port 8000

# Or using Make
make start
```

Access the API at `http://localhost:8000/docs`

---

## Docker Development

### Quick Start with Docker Compose
```bash
# Start all services (dev profile: PostgreSQL + Redis + pgAdmin)
docker-compose --profile dev up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Service Access Points

| Service | URL | Default Credentials |
|---------|-----|-------------------|
| API | http://localhost:8000 | - |
| Swagger | http://localhost:8000/docs | - |
| ReDoc | http://localhost:8000/redoc | - |
| PostgreSQL | localhost:5432 | user/password (see .env) |
| pgAdmin | http://localhost:5050 | admin@admin.com/admin |
| Redis | localhost:6379 | - |

### Database Access
```bash
# Connect to PostgreSQL via psql
psql -h localhost -U user -d request_system

# Or via Docker
docker exec -it request-system-db psql -U user -d request_system

# Via pgAdmin web interface
# http://localhost:5050
# Login: admin@admin.com / admin
# Add server: db:5432
```

---

## Common Development Tasks

### Database Operations

#### Initialize Database
```bash
# Create tables from schema
make init-db

# Or directly
python -m src.request_system.scripts.load_seed_data
```

#### Load Seed Data
```bash
# Load test data
make seed-db

# Or directly
python -c "from src.request_system.scripts.load_seed_data import load_seed_data; load_seed_data()"
```

#### Reset Database
```bash
# Drop all tables and recreate
make reset-db
```

#### View Database Schema
```bash
# List tables
docker exec request-system-db psql -U user -d request_system -c "\dt"

# List indexes
docker exec request-system-db psql -U user -d request_system -c "\di"
```

### Testing

#### Run All Tests
```bash
# Local tests
make test

# Or directly
pytest tests/ -v
```

#### Run Specific Test File
```bash
pytest tests/test_api.py -v
pytest tests/test_search_filtering.py -v
pytest tests/test_health_check.py -v
```

#### Run Specific Test Case
```bash
pytest tests/test_api.py::TestRequestAPI::test_create_request -v
```

#### Test with Coverage
```bash
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

#### Integration Tests Against Running Server
```bash
# Start server first
make start

# In another terminal, run integration tests
make test-remote

# Or with explicit server
API_BASE_URL=http://localhost:8000 pytest tests/test_remote_integration.py -v
```

### Running the Application

#### Development Mode
```bash
# With auto-reload on file changes
make start

# Or directly
python -m uvicorn src.request_system.presentation.main:app --reload
```

#### Production Mode
```bash
# Without reload
python -m uvicorn src.request_system.presentation.main:app --host 0.0.0.0 --port 8000
```

#### View Logs
```bash
# Docker services
docker-compose logs -f api

# Or all services
docker-compose logs -f
```

#### Stop Services
```bash
make stop

# Or
docker-compose down
```

### API Testing

#### Health Check
```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

#### List Requests
```bash
curl "http://localhost:8000/api/requests?limit=10"
```

#### Create Request
```bash
curl -X POST http://localhost:8000/api/requests \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "category_id": 1,
    "status_id": 1,
    "priority": 2,
    "title": "Test Request",
    "description": "This is a test",
    "account_name": "john.doe"
  }'
```

#### Search Requests
```bash
# Full-text search
curl "http://localhost:8000/api/requests?search=equipment"

# Filter by status
curl "http://localhost:8000/api/requests?status=submitted"

# Combine filters
curl "http://localhost:8000/api/requests?status=submitted&priority=3&sort_by=created_at&sort_order=desc&limit=5"
```

#### Get Single Request
```bash
curl http://localhost:8000/api/requests/1
```

#### Update Request
```bash
curl -X PATCH http://localhost:8000/api/requests/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

#### Change Status
```bash
curl -X PUT http://localhost:8000/api/requests/1/status \
  -H "Content-Type: application/json" \
  -d '{"status_id": 2}'
```

### Manual Testing with Postman

1. Import collection: `postman/Request-System-API.json`
2. Create environment with variables:
   - `base_url`: `http://localhost:8000`
3. Use predefined requests

---

## Code Structure

### Key Directories

```
src/request_system/
├── presentation/          # API & CLI (user-facing)
│   ├── main.py           # FastAPI app initialization
│   ├── api.py            # API endpoints
│   └── cli.py            # CLI commands
├── application/          # Business logic & services
│   ├── services/
│   │   ├── request_service.py    # Request operations
│   │   └── health_service.py     # Health monitoring
│   └── ports/            # Interfaces
│       ├── repositories.py       # Repository contracts
│       └── unit_of_work.py       # UoW contract
├── domain/               # Core domain models
│   ├── models.py         # Request, User, Category, etc.
│   └── events.py         # Domain events
└── infrastructure/       # Implementations
    ├── config.py         # Configuration
    ├── sqlite_adapter.py # SQLite implementation
    └── postgres_adapter.py # PostgreSQL implementation
```

### Service Layer

**RequestService** (`src/request_system/application/services/request_service.py`)
- `create_request()` - Create new request
- `get_request()` - Get by ID
- `list_requests()` - Simple listing
- `list_requests_with_filters()` - Advanced search/filter/sort/paginate
- `update_request()` - Update request
- `change_status()` - Change request status

**HealthCheckService** (`src/request_system/application/services/health_service.py`)
- `get_health_status()` - Full health report
- `check_readiness()` - Simple readiness check

### Models

**Request** (domain entity)
```python
class Request:
    id: int
    user_id: int
    category_id: int
    status_id: int
    priority: int (1-5)
    title: str
    description: str
    account_name: str
    created_at: datetime
    updated_at: datetime
```

**Request Pydantic Models** (for API)
```python
class RequestCreate(BaseModel):  # POST request body
class RequestUpdate(BaseModel):  # PATCH request body
class RequestResponse(BaseModel) # API response
class ListRequestsResponse(BaseModel)  # List response with metadata
```

---

## Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
git checkout -b fix/bug-name
```

### 2. Make Changes
- Update code in `src/request_system/`
- Write or update tests in `tests/`
- Update documentation in `docs/`

### 3. Run Tests
```bash
make test
pytest tests/ -v
```

### 4. Check Code Quality
```bash
# Run linting
pylint src/

# Run type checking (optional)
mypy src/
```

### 5. Commit Changes
```bash
git add .
git commit -m "feature: Add new feature

Detailed description of changes"
```

### 6. Push & Create Pull Request
```bash
git push origin feature/your-feature-name
# Create PR on GitHub
```

### 7. After Merge
```bash
git checkout main
git pull origin main
git branch -d feature/your-feature-name
```

---

## Adding New Features

### Adding New API Endpoint

1. **Create service method** in `RequestService`:
```python
def new_operation(self, params) -> Result:
    # Implementation
    pass
```

2. **Create Pydantic models** in `src/request_system/presentation/api.py`:
```python
class NewRequest(BaseModel):
    field: str

class NewResponse(BaseModel):
    result: str
```

3. **Add API endpoint** in `src/request_system/presentation/api.py`:
```python
@app.post("/api/new-operation")
async def new_operation(request: NewRequest) -> NewResponse:
    result = service.new_operation(request.field)
    return NewResponse(result=result)
```

4. **Add tests** in `tests/test_api.py`:
```python
def test_new_operation():
    response = client.post("/api/new-operation", json={"field": "value"})
    assert response.status_code == 200
    assert response.json()["result"] == "expected"
```

### Adding New Service Method

1. **Define method signature** in service interface
2. **Implement in service class**
3. **Write tests** for the method
4. **Document with docstring**

Example:
```python
def search_requests(self, query: str, limit: int = 10) -> List[Request]:
    """Search requests by full-text query.
    
    Args:
        query: Search query string
        limit: Maximum results to return (default: 10)
        
    Returns:
        List of matching requests
        
    Raises:
        ValueError: If query is empty or limit invalid
    """
    # Implementation
```

---

## Debugging

### Enable Debug Mode
```bash
# Set environment variable
export DEBUG=1
make start

# Or in docker-compose
DEBUG=1 docker-compose up
```

### View Detailed Logs
```bash
# Local development
python -m uvicorn src.request_system.presentation.main:app --log-level debug

# Docker
docker-compose logs -f --tail=100 api
```

### Database Debugging
```bash
# Connect to database
docker exec -it request-system-db psql -U user -d request_system

# Query tables
SELECT * FROM requests LIMIT 5;
SELECT * FROM users;
SELECT * FROM categories;

# Check migrations status
# (Uses Alembic)
```

### Breakpoint Debugging
```python
# In your code
import pdb; pdb.set_trace()

# Run with interactive output
python -m pdb src/request_system/presentation/main.py
```

---

## Environment Variables

### Development (.env)
```bash
APP_ENV=development
APP_DEBUG=true
DATABASE_URL=sqlite:///app.db
ALLOWED_HOSTS=localhost,127.0.0.1
SECRET_KEY=dev-secret-key
```

### Docker (.env.docker)
```bash
APP_ENV=development
DATABASE_URL=postgresql://user:password@db:5432/request_system
REDIS_URL=redis://cache:6379/0
```

### Production (.env.prod)
```bash
APP_ENV=production
APP_DEBUG=false
DATABASE_URL=postgresql://user:secure-password@prod-db:5432/request_system
SECRET_KEY=production-secret-key
ALLOWED_HOSTS=api.example.com
```

See `.env.example` files for all available variables.

---

## Performance Tips

### Database Optimization
- Use indexed fields for filtering
- Limit result sets with pagination
- Consider caching frequent queries

### API Performance
- Use pagination for large result sets
- Implement caching for read-heavy endpoints
- Monitor slow queries with logging

### Docker Performance
- Use production image (smaller, no dev deps)
- Enable layer caching by not changing requirements often
- Use volume mounts only for development

---

## Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
APP_PORT=8001 docker-compose up
```

**Database Connection Error**
```bash
# Check services are running
docker-compose ps

# View database logs
docker-compose logs db

# Test connection
docker exec request-system-db pg_isready
```

**Import Errors**
```bash
# Ensure package installed in editable mode
python -m pip install -e .

# Check PYTHONPATH
export PYTHONPATH=/path/to/project:$PYTHONPATH
```

**Tests Failing**
```bash
# Run with verbose output
pytest tests/ -vv -s

# Check database is initialized
make init-db

# Reset everything
make reset-db
make init-db
pytest tests/ -v
```

### Getting Help
1. Check `docs/` directory for guides
2. View test cases for usage examples
3. Read source code comments
4. Check GitHub Issues
5. Create new issue for bugs

---

## Useful Commands

### One-Line Shortcuts
```bash
# Quick start
make start

# Full reset and test
make reset-db && make init-db && make test

# Deploy locally
docker-compose --profile dev up -d

# View all endpoints
curl http://localhost:8000/openapi.json | python -m json.tool

# Watch logs
docker-compose logs -f api

# Database backup
make backup

# Restore from backup
make restore BACKUP_FILE=backup_20261115.db
```

### Makefile Commands
Run `make help` to see all available commands:

- `make start` - Start services
- `make stop` - Stop services
- `make logs` - View application logs
- `make test` - Run all tests
- `make init-db` - Initialize database
- `make seed-db` - Load seed data
- `make reset-db` - Reset database
- `make deploy-vps` - Deploy to VPS
- `make verify-local` - Verify local deployment
- `make verify-remote` - Verify remote deployment

---

## Contributing

1. **Branch naming:** `feature/description` or `fix/description`
2. **Commit messages:** Descriptive, present tense
3. **Tests required:** All new features need tests
4. **Documentation:** Update docs/ for significant changes
5. **Code style:** Follow existing conventions

---

## Resources

### Documentation
- [LAB8_FINAL_REPORT.md](../LAB8_FINAL_REPORT.md) - Comprehensive Lab 8 report
- [DEPLOYMENT.md](../docs/DEPLOYMENT.md) - Deployment guide
- [VERIFICATION.md](../docs/VERIFICATION.md) - Testing procedures
- [DATABASE_SCHEMA.md](../docs/DATABASE_SCHEMA.md) - Database structure

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Pydantic Validation](https://docs.pydantic.dev/)
- [Pytest Testing](https://docs.pytest.org/)
- [Docker Documentation](https://docs.docker.com/)

### Tools & Services
- Postman Collection: `postman/Request-System-API.json`
- API Docs: `http://localhost:8000/docs` (Swagger UI)
- ReDoc: `http://localhost:8000/redoc`
- pgAdmin: `http://localhost:5050` (PostgreSQL management)

---

## Contact

For questions or issues:
- Create GitHub Issue
- Check existing documentation
- Review test cases for examples
- Ask in team chat

---

**Happy Coding!** 🚀

---

Generated: 2026-11-15  
Document: Developers Guide  
Lab: Lab 8 - Docker Infrastructure & Deployment  
Status: ✅ Complete
