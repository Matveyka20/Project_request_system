#!/bin/bash
# Quick deployment status summary

echo "📋 Deployment Status"
echo "===================="
echo ""

if [ -f deployment-config.json ]; then
    python3 << 'PYTHON_SCRIPT'
import json

try:
    with open('deployment-config.json', 'r') as f:
        config = json.load(f)
    
    deploy = config['deployment']
    address = deploy['server']['address']
    timestamp = deploy['timestamp']
    environment = deploy['environment']['type']
    status = deploy['health_check']['status']
    
    print(f"Address:     {address}")
    print(f"Date:        {timestamp}")
    print(f"Environment: {environment}")
    print(f"Status:      {status}")
    print("")
    
    if address != "TBD":
        print("📌 Endpoints:")
        print(f"  - API:       http://{address}:8000")
        print(f"  - Docs:      http://{address}:8000/docs")
        print(f"  - Health:    http://{address}:8000/health")
        print(f"  - ReDoc:     http://{address}:8000/redoc")
    else:
        print("⚠️  Application address not yet configured")
    
except Exception as e:
    print(f"❌ Error: {e}")
PYTHON_SCRIPT
else
    echo "❌ No deployment registered yet"
    echo ""
    echo "Register deployment:"
    echo "  bash scripts/register-deployment.sh <address>"
    echo ""
    echo "Example:"
    echo "  bash scripts/register-deployment.sh 192.168.1.100 2026-11-15 production DigitalOcean 'Ubuntu 20.04'"
fi
