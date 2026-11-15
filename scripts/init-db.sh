#!/bin/bash
# Database initialization script for Request System
# Initializes database schema and loads seed data
#
# Usage:
#   bash scripts/init-db.sh                 - Initialize with seed data
#   bash scripts/init-db.sh --reset         - Reset database first
#   bash scripts/init-db.sh --database FILE - Use custom database path
#
# Environment variables:
#   REQUEST_SYSTEM_DB - Path to database file (default: requests.db)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
RESET_DB=false
DB_PATH="${REQUEST_SYSTEM_DB:-requests.db}"

while [[ $# -gt 0 ]]; do
    case $1 in
        --reset)
            RESET_DB=true
            shift
            ;;
        --database)
            DB_PATH="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# ============================================================================
# Header
# ============================================================================
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Request System - Database Initialization${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# ============================================================================
# Check Python availability
# ============================================================================
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

PY_VERSION=$(python3 --version 2>&1)
echo -e "${GREEN}✓${NC} Python 3 found: $PY_VERSION"

# ============================================================================
# Reset database if requested
# ============================================================================
if [ "$RESET_DB" = true ]; then
    if [ -f "$DB_PATH" ]; then
        echo -e "${YELLOW}⚠️  Resetting database...${NC}"
        rm -f "$DB_PATH"
        echo -e "${GREEN}✓${NC} Database file deleted: $DB_PATH"
    fi
fi

# ============================================================================
# Initialize database and load seed data
# ============================================================================
echo ""
echo -e "${BLUE}📝 Initializing database schema...${NC}"

python3 -m request_system.scripts.load_seed_data \
    --database "$DB_PATH" \
    $([ "$RESET_DB" = true ] && echo "--reset-db" || echo "")

# ============================================================================
# Verify initialization
# ============================================================================
echo ""
echo -e "${BLUE}🔍 Verifying database initialization...${NC}"

if ! [ -f "$DB_PATH" ]; then
    echo -e "${RED}❌ Database file not found: $DB_PATH${NC}"
    exit 1
fi

DB_SIZE=$(du -h "$DB_PATH" | cut -f1)
echo -e "${GREEN}✓${NC} Database file exists: $DB_PATH (Size: $DB_SIZE)"

# Check tables count
TABLE_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" 2>/dev/null || echo "0")
echo -e "${GREEN}✓${NC} Tables created: $TABLE_COUNT"

# Check data count
USER_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM Users;" 2>/dev/null || echo "0")
REQUEST_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM Requests;" 2>/dev/null || echo "0")
CATEGORY_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM Categories;" 2>/dev/null || echo "0")
STATUS_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM Statuses;" 2>/dev/null || echo "0")

echo -e "${GREEN}✓${NC} Users: $USER_COUNT"
echo -e "${GREEN}✓${NC} Requests: $REQUEST_COUNT"
echo -e "${GREEN}✓${NC} Categories: $CATEGORY_COUNT"
echo -e "${GREEN}✓${NC} Statuses: $STATUS_COUNT"

# ============================================================================
# Summary
# ============================================================================
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Database initialization completed successfully!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo "  1. Start the application: make run"
echo "  2. View API docs: http://localhost:8000/docs"
echo "  3. Access database: sqlite3 $DB_PATH"
echo ""

exit 0
