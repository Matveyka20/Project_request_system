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
	@echo "  make backup       - Backup PostgreSQL database"
	@echo "  make restore      - Restore from backup (requires BACKUP_FILE)"
	@echo "  make db-shell     - Access PostgreSQL shell"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        - Remove containers and volumes"
	@echo "  make update       - Pull latest code and restart"
	@echo ""
	@echo "Examples:"
	@echo "  make logs                            # Follow app logs"
	@echo "  make health                          # Check health"
	@echo "  make backup                          # Create backup"
	@echo "  make restore BACKUP_FILE=backup.sql  # Restore backup"

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

# Database backup
backup:
	@TIMESTAMP=$$(date +%Y%m%d_%H%M%S); \
	echo "Creating backup: backup_$$TIMESTAMP.sql"; \
	docker-compose exec -T db pg_dump -U postgres requests_db > backup_$$TIMESTAMP.sql; \
	gzip backup_$$TIMESTAMP.sql; \
	echo "Backup created: backup_$$TIMESTAMP.sql.gz"

# Database restore
restore:
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "Error: BACKUP_FILE not specified"; \
		echo "Usage: make restore BACKUP_FILE=backup_20241115.sql"; \
		exit 1; \
	fi
	@echo "Restoring from: $(BACKUP_FILE)"
	@if [ "$$(echo $(BACKUP_FILE) | grep -c '.gz$$')" -eq 1 ]; then \
		gunzip -c $(BACKUP_FILE) | docker-compose exec -T db psql -U postgres requests_db; \
	else \
		docker-compose exec -T db psql -U postgres requests_db < $(BACKUP_FILE); \
	fi
	@echo "Database restored"

# Database shell
db-shell:
	docker-compose exec db psql -U postgres -d requests_db

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
