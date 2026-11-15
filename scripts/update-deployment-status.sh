#!/bin/bash
# Update deployment status and health check

APP_ADDRESS=${1:-localhost:8000}

echo "🔍 Checking deployment status for: $APP_ADDRESS"
echo ""

# Check health endpoint
echo "⏳ Checking /health endpoint..."
HEALTH_RESPONSE=$(curl -s http://$APP_ADDRESS/health 2>/dev/null || echo '{"error":"Connection failed"}')
HEALTH_STATUS=$(echo $HEALTH_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "unknown")

echo "Response: $HEALTH_RESPONSE"
echo ""

# Update config using Python
python3 << PYTHON_SCRIPT
import json
from datetime import datetime

try:
    with open('deployment-config.json', 'r') as f:
        config = json.load(f)
    
    # Update status
    config['deployment']['server']['address'] = "$APP_ADDRESS"
    config['deployment']['health_check']['status'] = "$HEALTH_STATUS"
    config['deployment']['health_check']['last_check'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    with open('deployment-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Status updated:")
    print(f"   Address:    $APP_ADDRESS")
    print(f"   Health:     $HEALTH_STATUS")
    print(f"   Last Check: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
except Exception as e:
    print(f"❌ Error updating status: {e}")
    exit(1)
PYTHON_SCRIPT
