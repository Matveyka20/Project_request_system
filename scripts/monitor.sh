#!/bin/bash
# Health Monitoring Script for Request System
# Continuously monitors application health and logs status
# Usage: ./scripts/monitor.sh

set -e

# Configuration
APP_PORT="${APP_PORT:-8000}"
CHECK_INTERVAL="${CHECK_INTERVAL:-60}"  # Seconds between checks
LOG_FILE="${LOG_FILE:-./health-monitor.log}"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Initialize
mkdir -p "$(dirname "$LOG_FILE")"

echo -e "${BLUE}[INFO]${NC} Health Monitoring Started"
echo -e "${BLUE}[INFO]${NC} Interval: ${CHECK_INTERVAL}s | Log: $LOG_FILE"
echo ""

# Counter for tracking state changes
LAST_STATUS=""
CONSECUTIVE_FAILURES=0
MAX_FAILURES=3

# Signal handler for graceful shutdown
trap 'echo ""; echo -e "${BLUE}[INFO]${NC} Monitoring stopped"; exit 0' SIGINT SIGTERM

# Main monitoring loop
while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Fetch health status
    RESPONSE=$(curl -s -m 5 http://localhost:$APP_PORT/health 2>/dev/null || echo "")
    
    if [ -z "$RESPONSE" ]; then
        STATUS="error"
        MESSAGE="Connection refused"
        CONSECUTIVE_FAILURES=$((CONSECUTIVE_FAILURES + 1))
    else
        # Extract status from JSON response
        STATUS=$(echo "$RESPONSE" | jq -r '.status // "unknown"' 2>/dev/null || echo "unknown")
        UPTIME=$(echo "$RESPONSE" | jq -r '.uptime_seconds // "?"' 2>/dev/null || echo "?")
        DB_STATUS=$(echo "$RESPONSE" | jq -r '.database // "?"' 2>/dev/null || echo "?")
        
        case "$STATUS" in
            "healthy")
                MESSAGE="✅ Healthy (uptime: ${UPTIME}s, db: $DB_STATUS)"
                CONSECUTIVE_FAILURES=0
                ;;
            "degraded")
                MESSAGE="⚠️  Degraded (uptime: ${UPTIME}s, db: $DB_STATUS)"
                CONSECUTIVE_FAILURES=0
                ;;
            "unhealthy")
                MESSAGE="❌ Unhealthy (db: $DB_STATUS)"
                CONSECUTIVE_FAILURES=$((CONSECUTIVE_FAILURES + 1))
                ;;
            *)
                MESSAGE="❓ Unknown status"
                CONSECUTIVE_FAILURES=$((CONSECUTIVE_FAILURES + 1))
                ;;
        esac
    fi
    
    # Log to file
    echo "[$TIMESTAMP] Status: $STATUS | $MESSAGE" >> "$LOG_FILE"
    
    # Display status
    if [ "$STATUS" = "$LAST_STATUS" ]; then
        # Same status, compact output
        printf "\r${BLUE}[%s]${NC} %s" "$TIMESTAMP" "$MESSAGE"
    else
        # Status changed
        echo ""
        printf "${BLUE}[%s]${NC} %s" "$TIMESTAMP" "$MESSAGE"
        LAST_STATUS="$STATUS"
    fi
    
    # Alert on consecutive failures
    if [ "$CONSECUTIVE_FAILURES" -ge "$MAX_FAILURES" ]; then
        echo ""
        echo -e "${RED}[ALERT]${NC} Service unhealthy for $CONSECUTIVE_FAILURES consecutive checks!"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ALERT: Consecutive failures: $CONSECUTIVE_FAILURES" >> "$LOG_FILE"
        
        # Optional: Send alert (webhook, email, etc.)
        # curl -X POST https://your-alert-service.com/notify \
        #   -d "service=request-system&status=$STATUS&failures=$CONSECUTIVE_FAILURES"
    fi
    
    # Wait for next check
    sleep "$CHECK_INTERVAL"
done
