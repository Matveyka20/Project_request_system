# Makefile for Request System API
# Useful commands for development and deployment

.PHONY: help build up down restart logs status health clean backup restore dev prod

# Default target
help:
	@echo "Request System API - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start in development mode"
	@echo "  make build        - Build Docker image"
	@echo ""
	@echo "Operations:"
	@echo "  make up           - Start all services"
	@echo "  make down         - Stop all services"
	@echo "  make restart      - Restart services"
	@echo "  make ps           - Show services status"
	@echo ""
	@echo "Monitoring:"
	@echo "  make logs         - View application logs (follow)"
	@echo "  make health       - Check health endpoint"
	@echo "  make status       - Show service status"
	@echo "  make monitor      - Run health monitor script"
	@echo ""
	@echo "Database:"
	@echo "  make init-db      - Initialize database with schema and seed data"
	@echo "  make reset-db     - Reset database (delete and reinitialize)"
	@echo "  make seed-db      - Load seed data into existing database"
	@echo "  make backup       - Backup SQLite database"
	@echo "  make restore      - Restore from backup (requires BACKUP_FILE)"
	@echo "  make db-shell     - Access SQLite database shell"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        - Remove containers and volumes"
	@echo "  make update       - Pull latest code and restart"
	@echo ""
	@echo "Examples:"
	@echo "  make logs                            # Follow app logs"
	@echo "  make health                          # Check health"
	@echo "  make init-db                         # Initialize database"
	@echo "  make backup                          # Create backup"
	@echo "  make restore BACKUP_FILE=backup.db   # Restore backup"

# Build
build:
	docker-compose build app

# Development mode
dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "Development environment started"
	@echo "Access at: http://localhost:8000/docs"

# Production mode
prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "Production environment started"

# Start services
up:
	docker-compose up -d
	@echo "Services started"
	@sleep 5
	@$(MAKE) health

# Stop services
down:
	docker-compose down
	@echo "Services stopped"

# Restart services
restart:
	docker-compose restart
	@echo "Services restarted"

# Show processes
ps:
	docker-compose ps

# View logs
logs:
	docker-compose logs -f app

# View all logs
logs-all:
	docker-compose logs -f

# Health check
health:
	@curl -s http://localhost:8000/health | jq .

# Show status
status:
	@echo "Container Status:"
	@docker-compose ps
	@echo ""
	@echo "Health Status:"
	@$(MAKE) health

# Monitor health
monitor:
	bash scripts/monitor.sh

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Database Commands
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Initialize database with schema and seed data
init-db:
	@echo "Initializing database with schema and seed data..."
	bash scripts/init-db.sh

# Reset database (delete and reinitialize)
reset-db:
	@echo "Resetting database..."
	bash scripts/init-db.sh --reset

# Load seed data into existing database
seed-db:
	@echo "Loading seed data..."
	python3 -m request_system.scripts.load_seed_data

# Database backup
backup:
	@TIMESTAMP=$$(date +%Y%m%d_%H%M%S); \
	echo "Creating backup: requests_$$TIMESTAMP.db"; \
	cp requests.db backup_requests_$$TIMESTAMP.db; \
	gzip backup_requests_$$TIMESTAMP.db; \
	echo "Backup created: backup_requests_$$TIMESTAMP.db.gz"

# Database restore
restore:
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "Error: BACKUP_FILE not specified"; \
		echo "Usage: make restore BACKUP_FILE=backup_20241115.db"; \
		exit 1; \
	fi
	@echo "Restoring from: $(BACKUP_FILE)"
	@if [ "$$(echo $(BACKUP_FILE) | grep -c '.gz$$')" -eq 1 ]; then \
		gunzip -c $(BACKUP_FILE) > requests.db; \
	else \
		cp $(BACKUP_FILE) requests.db; \
	fi
	@echo "Database restored from $(BACKUP_FILE)"

# Database shell
db-shell:
	sqlite3 requests.db

# Database stats
db-stats:
	@sqlite3 requests.db "SELECT 'Users' as table_name, COUNT(*) as count FROM Users UNION ALL SELECT 'Requests', COUNT(*) FROM Requests UNION ALL SELECT 'Comments', COUNT(*) FROM Comments UNION ALL SELECT 'Categories', COUNT(*) FROM Categories UNION ALL SELECT 'Statuses', COUNT(*) FROM Statuses;"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Remote Deployment Commands
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Clean up
clean:
	@echo "Removing containers and volumes..."
	docker-compose down -v
	@echo "Cleanup complete"

# Update application
update:
	@echo "Pulling latest code..."
	git pull origin theodore/develop
	@echo "Rebuilding image..."
	docker-compose build app
	@echo "Restarting services..."
	docker-compose up -d
	@echo "Update complete"
	@sleep 5
	@$(MAKE) health

# Database stats
db-stats:
	docker-compose exec db psql -U postgres -d requests_db -c "SELECT COUNT(*) as total_requests FROM requests;"

# Container resource usage
stats:
	docker stats --no-stream

# Test API
test-api:
	@echo "Testing API endpoints..."
	@echo ""
	@echo "1. Health check:"
	@curl -s http://localhost:8000/health | jq .
	@echo ""
	@echo "2. Ready check:"
	@curl -s http://localhost:8000/ready | jq .
	@echo ""
	@echo "3. Get requests:"
	@curl -s http://localhost:8000/api/requests | jq '.items | length' || echo "No requests"

# View environment
show-env:
	@echo "Environment Configuration (.env):"
	@grep -E "^[^#]" .env | head -20

# Disk usage
disk:
	docker system df

# Prune unused resources
prune:
	@echo "Cleaning up unused Docker resources..."
	docker system prune -f
	@echo "Cleanup complete"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Database Commands
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Initialize database with schema and seed data
init-db:
	@echo "Initializing database with schema and seed data..."
	bash scripts/init-db.sh

# Reset database (delete and reinitialize)
reset-db:
	@echo "Resetting database..."
	bash scripts/init-db.sh --reset

# Load seed data into existing database
seed-db:
	@echo "Loading seed data..."
	python3 -m request_system.scripts.load_seed_data

# Database backup
backup:
	@TIMESTAMP=$$(date +%Y%m%d_%H%M%S); \
	echo "Creating backup: requests_$$TIMESTAMP.db"; \
	cp requests.db backup_requests_$$TIMESTAMP.db; \
	gzip backup_requests_$$TIMESTAMP.db; \
	echo "Backup created: backup_requests_$$TIMESTAMP.db.gz"

# Database restore
restore:
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "Error: BACKUP_FILE not specified"; \
		echo "Usage: make restore BACKUP_FILE=backup_20241115.db"; \
		exit 1; \
	fi
	@echo "Restoring from: $(BACKUP_FILE)"
	@if [ "$$(echo $(BACKUP_FILE) | grep -c '.gz$$')" -eq 1 ]; then \
		gunzip -c $(BACKUP_FILE) > requests.db; \
	else \
		cp $(BACKUP_FILE) requests.db; \
	fi
	@echo "Database restored from $(BACKUP_FILE)"

# Database shell
db-shell:
	sqlite3 requests.db

# Database stats
db-stats:
	@sqlite3 requests.db "SELECT 'Users' as table_name, COUNT(*) as count FROM Users UNION ALL SELECT 'Requests', COUNT(*) FROM Requests UNION ALL SELECT 'Comments', COUNT(*) FROM Comments UNION ALL SELECT 'Categories', COUNT(*) FROM Categories UNION ALL SELECT 'Statuses', COUNT(*) FROM Statuses;"

# ?????????????????????????????????????????????????????????????????
# Verification & Testing Commands
# ?????????????????????????????????????????????????????????????????

# Verify local deployment
verify-local:
	@echo "Verifying local API deployment..."
	bash scripts/remote-verify.sh localhost 8000

# Verify remote deployment
verify-remote:
	@read -p "Enter VPS IP: " ip; \
	read -p "Enter API Port (default 8000): " port; \
	port={port:-8000}; \
	bash scripts/remote-verify.sh ip port

# Full deployment and verification
deploy-and-verify:
	@read -p "Enter VPS IP: " ip; \
	read -p "Enter VPS User (default ubuntu): " user; \
	user={user:-ubuntu}; \
	read -p "Enter SSH Port (default 22): " port; \
	port={port:-22}; \
	bash scripts/full-deploy-and-verify.sh ip user port

# Run integration tests
test-remote:
	@echo "Running integration tests..."
	pytest tests/test_remote_integration.py -v --tb=short

# Run integration tests with coverage
test-remote-coverage:
	@echo "Running integration tests with coverage..."
	pytest tests/test_remote_integration.py -v --cov=src --cov-report=html --cov-report=term

# Run integration tests against remote API
test-remote-server:
	@read -p "Enter API base URL (e.g., http://192.168.1.100:8000): " url; \
	API_BASE_URL=url pytest tests/test_remote_integration.py -v --tb=short

# Generate verification report
verify-report:
	@read -p "Enter Server IP: " ip; \
	read -p "Enter API Port (default 8000): " port; \
	port={port:-8000}; \
	bash scripts/generate-verification-report.sh ip port
