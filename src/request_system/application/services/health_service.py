"""Health check service for monitoring application status and service availability."""

import sys
import time
from datetime import datetime
from typing import Optional

from src.request_system.presentation.models import HealthCheckResponse


class HealthCheckService:
    """Service for checking application health and service status."""

    def __init__(self):
        """Initialize health check service with start time."""
        self.start_time = time.time()

    async def check_health(self, config) -> HealthCheckResponse:
        """
        Check application health and return detailed status.

        Checks:
        - Database connectivity
        - Cache (Redis) connectivity if configured
        - Application uptime

        Args:
            config: Settings configuration object

        Returns:
            HealthCheckResponse with status, service checks, and metadata
        """
        # Calculate uptime
        uptime = time.time() - self.start_time

        # Check database
        db_status = await self._check_database()

        # Check cache (if enabled)
        cache_status = await self._check_cache(config)

        # Determine overall status
        # unhealthy = critical services down
        # degraded = some services not working but app still responsive
        # healthy = all systems ok
        if db_status == "error":
            status = "unhealthy"
        elif cache_status == "error":
            status = "degraded"
        else:
            status = "healthy"

        return HealthCheckResponse(
            status=status,
            version="1.1.0",
            timestamp=datetime.utcnow(),
            uptime_seconds=uptime,
            database=db_status,
            cache=cache_status,
            environment=config.app_env,
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )

    async def _check_database(self) -> str:
        """
        Check database connectivity.

        Returns:
            "ok" if database is accessible, "error" if not, "unknown" if check fails

        Note:
            Current implementation returns "ok" as a placeholder.
            TODO: Implement actual database connectivity check
        """
        try:
            # TODO: Implement actual database check
            # - For SQLite: check file existence and basic query
            # - For PostgreSQL: connect and run SELECT 1
            # For now, always return ok
            return "ok"
        except Exception as e:
            return "error"

    async def _check_cache(self, config) -> Optional[str]:
        """
        Check cache (Redis) connectivity if configured.

        Args:
            config: Settings configuration object

        Returns:
            "ok" if cache is accessible, "error" if not, None if not configured

        Note:
            Current implementation returns None or "ok" as a placeholder.
            TODO: Implement Redis connectivity check
        """
        # Return None if Redis is not configured
        if not config.redis_url or config.redis_url.strip() == "":
            return None

        try:
            # TODO: Implement actual Redis check
            # - Connect to Redis
            # - Run PING command
            # For now, always return ok if configured
            return "ok"
        except Exception as e:
            return "error"


# Global singleton instance
health_service = HealthCheckService()
