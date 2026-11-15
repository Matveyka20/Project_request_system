#!/bin/bash
# Register/record a deployment

set -e

APP_ADDRESS=${1:-}
DEPLOY_DATE=${2:-$(date -u +'%Y-%m-%dT%H:%M:%SZ')}
ENVIRONMENT=${3:-production}
VPS_PROVIDER=${4:-}
OS_VERSION=${5:-}

if [ -z "$APP_ADDRESS" ]; then
    echo "❌ Error: Application address is required"
    echo "Usage: bash scripts/register-deployment.sh <address> [date] [environment] [provider] [os]"
    echo "Example: bash scripts/register-deployment.sh 192.168.1.100 2026-11-15 production DigitalOcean 'Ubuntu 20.04'"
    exit 1
fi

echo "📝 Registering deployment..."
echo "Application Address: $APP_ADDRESS"
echo "Deploy Date: $DEPLOY_DATE"
echo "Environment: $ENVIRONMENT"
echo "VPS Provider: $VPS_PROVIDER"
echo "OS: $OS_VERSION"
echo ""

# Update deployment-config.json using Python (more portable than jq)
python3 << 'PYTHON_SCRIPT'
import json
import sys
from datetime import datetime

try:
    with open('deployment-config.json', 'r') as f:
        config = json.load(f)
    
    # Update deployment info
    config['deployment']['server']['address'] = sys.argv[1]
    config['deployment']['server']['ip'] = sys.argv[1]
    config['deployment']['timestamp'] = sys.argv[2]
    config['deployment']['environment']['type'] = sys.argv[3]
    config['deployment']['server']['provider'] = sys.argv[4]
    config['deployment']['environment']['os_version'] = sys.argv[5]
    config['deployment']['health_check']['url'] = f"http://{sys.argv[1]}:8000/health"
    
    with open('deployment-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ deployment-config.json updated")
except Exception as e:
    print(f"❌ Error updating config: {e}")
    sys.exit(1)
PYTHON_SCRIPT

# Append to DEPLOYMENT_HISTORY.md
cat >> DEPLOYMENT_HISTORY.md << EOF

### Deployment on $DEPLOY_DATE
- **Address**: http://$APP_ADDRESS:8000
- **Environment**: $ENVIRONMENT
- **VPS Provider**: $VPS_PROVIDER
- **OS**: $OS_VERSION
- **Status**: ✅ Registered
- **Swagger UI**: http://$APP_ADDRESS:8000/docs
- **Health Check**: http://$APP_ADDRESS:8000/health

EOF

echo "✅ Deployment registered successfully!"
echo ""
echo "Files updated:"
echo "  - deployment-config.json"
echo "  - DEPLOYMENT_HISTORY.md"
echo ""
echo "Access points:"
echo "  - API:       http://$APP_ADDRESS:8000"
echo "  - Docs:      http://$APP_ADDRESS:8000/docs"
echo "  - Health:    http://$APP_ADDRESS:8000/health"
