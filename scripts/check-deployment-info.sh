#!/bin/bash
# Display current deployment information

echo "=== Current Deployment Information ==="
echo ""

if [ -f deployment-config.json ]; then
    python3 << 'PYTHON_SCRIPT'
import json
import sys

try:
    with open('deployment-config.json', 'r') as f:
        config = json.load(f)
    
    deploy = config['deployment']
    
    echo "📍 Server Information"
    echo "===================="
    print(f"  Address:      {deploy['server']['address']}")
    print(f"  IP:           {deploy['server']['ip']}")
    print(f"  Domain:       {deploy['server']['domain']}")
    print(f"  Port:         {deploy['server']['port']}")
    print(f"  Provider:     {deploy['server']['provider']}")
    print(f"  Region:       {deploy['server']['region']}")
    print("")
    
    print("🔧 Application")
    print("===============")
    print(f"  Name:         {deploy['application']['name']}")
    print(f"  Version:      {deploy['application']['version']}")
    print(f"  Phase:        {deploy['application']['phase']}")
    print(f"  Deployed:     {deploy['timestamp']}")
    print("")
    
    print("🖥️  Environment")
    print("================")
    print(f"  Type:         {deploy['environment']['type']}")
    print(f"  OS:           {deploy['environment']['os']} {deploy['environment']['os_version']}")
    print(f"  Python:       {deploy['environment']['python_version']}")
    print(f"  Docker:       {deploy['environment']['docker_version']}")
    print("")
    
    print("🚀 Services Status")
    print("==================")
    for service, info in deploy['services'].items():
        status = "✅" if info['status'] == 'running' else "⚠️"
        print(f"  {status} {service.upper():12} {info.get('port', 'N/A')} (internal)")
    print("")
    
    print("📊 Database Status")
    print("==================")
    db = deploy['database']
    print(f"  Initialized:       {db['initialized']}")
    print(f"  Migrations:        {db['migrations_applied']}")
    print(f"  Seed Data:         {db['seed_data_loaded']}")
    print(f"  Requests:          {db['total_requests']}")
    print(f"  Users:             {db['total_users']}")
    print("")
    
    print("🔒 SSL/HTTPS")
    print("=============")
    ssl = deploy['ssl']
    print(f"  Enabled:           {ssl['enabled']}")
    print(f"  Certificate:       {ssl['certificate_type']}")
    print(f"  Domain:            {ssl['domain']}")
    print("")
    
    print("❤️  Health Check")
    print("================")
    health = deploy['health_check']
    print(f"  URL:               {health['url']}")
    print(f"  Status:            {health['status']}")
    print(f"  Last Check:        {health['last_check']}")
    print("")
    
    print("📝 Deployment Info")
    print("==================")
    print(f"  Method:            {deploy['deployment_method']}")
    print(f"  Deployed By:       {deploy['deployed_by']}")
    print(f"  Notes:             {deploy['notes']}")
    
except json.JSONDecodeError as e:
    print(f"❌ Invalid JSON in deployment-config.json: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error reading deployment info: {e}")
    sys.exit(1)
PYTHON_SCRIPT
else
    echo "❌ No deployment-config.json found"
    echo "Run: bash scripts/register-deployment.sh <address> to register"
fi

echo ""
echo "=== Recent Deployments (from DEPLOYMENT_HISTORY.md) ==="
if [ -f DEPLOYMENT_HISTORY.md ]; then
    tail -20 DEPLOYMENT_HISTORY.md
else
    echo "No deployment history yet"
fi
