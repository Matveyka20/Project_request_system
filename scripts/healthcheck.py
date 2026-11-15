#!/usr/bin/env python
"""
Health check script for Docker Compose services.
Verifies that API, database, and cache are healthy.
"""

import sys
import time
import requests
from typing import Dict, Tuple
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_api_health(url: str = "http://localhost:8000/health", timeout: int = 5) -> Tuple[bool, str]:
    """Check API health endpoint."""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            version = data.get("version", "unknown")
            return True, f"API healthy (status={status}, version={version})"
        else:
            return False, f"API health check failed with status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "API connection failed (is it running?)"
    except requests.exceptions.Timeout:
        return False, "API request timed out"
    except Exception as e:
        return False, f"API health check error: {str(e)}"


def check_database_health(dsn: str = None, timeout: int = 5) -> Tuple[bool, str]:
    """Check database health (PostgreSQL or SQLite)."""
    try:
        import os
        
        if dsn is None:
            dsn = os.getenv("DATABASE_URL", "sqlite:///./requests.db")
        
        if dsn.startswith("sqlite"):
            # SQLite check
            db_path = dsn.replace("sqlite:///", "")
            if Path(db_path).exists():
                return True, f"SQLite database exists: {db_path}"
            else:
                return False, f"SQLite database not found: {db_path}"
        
        elif dsn.startswith("postgresql"):
            # PostgreSQL check
            import psycopg2
            
            try:
                conn = psycopg2.connect(dsn, connect_timeout=timeout)
                conn.close()
                return True, "PostgreSQL connection successful"
            except psycopg2.OperationalError as e:
                return False, f"PostgreSQL connection failed: {str(e)}"
        
        else:
            return False, f"Unknown database type: {dsn}"
    
    except ImportError:
        return False, "Database driver not installed"
    except Exception as e:
        return False, f"Database health check error: {str(e)}"


def check_redis_health(url: str = None, timeout: int = 5) -> Tuple[bool, str]:
    """Check Redis health."""
    try:
        import os
        import redis
        
        if url is None:
            url = os.getenv("REDIS_URL", "")
        
        if not url:
            return True, "Redis not configured (skipped)"
        
        client = redis.from_url(url, socket_connect_timeout=timeout)
        pong = client.ping()
        
        if pong:
            return True, "Redis connection successful"
        else:
            return False, "Redis ping failed"
    
    except ImportError:
        return False, "Redis driver not installed"
    except Exception as e:
        return False, f"Redis health check error: {str(e)}"


def main():
    """Run all health checks."""
    print("🔍 Checking services health...\n")
    
    checks = [
        ("API", check_api_health),
        ("Database", check_database_health),
        ("Redis", check_redis_health),
    ]
    
    results: Dict[str, bool] = {}
    
    for name, check_func in checks:
        try:
            healthy, message = check_func()
            status_symbol = "✓" if healthy else "✗"
            print(f"{status_symbol} {name}: {message}")
            results[name] = healthy
        except Exception as e:
            print(f"✗ {name}: Unexpected error: {str(e)}")
            results[name] = False
    
    # Summary
    print()
    healthy_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    if healthy_count == total_count:
        print(f"✓ All {total_count} services are healthy!")
        return 0
    else:
        print(f"✗ {total_count - healthy_count}/{total_count} services failed health check")
        return 1


if __name__ == "__main__":
    sys.exit(main())
