"""Tests for health check endpoints."""

import pytest
from datetime import datetime
from httpx import AsyncClient

from src.request_system.presentation.main import app


class TestHealthCheck:
    """Health check endpoint tests."""

    @pytest.mark.asyncio
    async def test_health_check_response_structure(self):
        """Test /health endpoint returns correct response structure."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")

            assert response.status_code == 200
            data = response.json()

            # Verify required fields
            assert "status" in data
            assert "version" in data
            assert "timestamp" in data
            assert "uptime_seconds" in data
            assert "database" in data
            assert "environment" in data
            assert "python_version" in data

    @pytest.mark.asyncio
    async def test_health_check_status_values(self):
        """Test /health endpoint returns valid status values."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            data = response.json()

            # Status must be one of these values
            assert data["status"] in ["healthy", "degraded", "unhealthy"]

    @pytest.mark.asyncio
    async def test_health_check_database_status(self):
        """Test /health endpoint includes database status."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            data = response.json()

            # Database status must be valid
            assert data["database"] in ["ok", "error", "unknown"]

    @pytest.mark.asyncio
    async def test_health_check_environment(self):
        """Test /health endpoint includes environment."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            data = response.json()

            # Environment must be one of these
            assert data["environment"] in ["development", "staging", "production"]

    @pytest.mark.asyncio
    async def test_health_check_version(self):
        """Test /health endpoint includes API version."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            data = response.json()

            # Version should match API version
            assert data["version"] == "1.1.0"

    @pytest.mark.asyncio
    async def test_health_check_uptime(self):
        """Test /health endpoint uptime is non-negative."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            data = response.json()

            # Uptime should be non-negative
            assert data["uptime_seconds"] >= 0

    @pytest.mark.asyncio
    async def test_health_check_timestamp_format(self):
        """Test /health endpoint timestamp is valid ISO format."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            data = response.json()

            # Timestamp should be parseable as ISO datetime
            try:
                datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
            except ValueError:
                pytest.fail(f"Timestamp {data['timestamp']} is not valid ISO format")

    @pytest.mark.asyncio
    async def test_health_check_python_version(self):
        """Test /health endpoint includes Python version."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            data = response.json()

            # Python version should be in format X.Y.Z
            parts = data["python_version"].split(".")
            assert len(parts) == 3
            for part in parts:
                assert part.isdigit()

    @pytest.mark.asyncio
    async def test_health_check_cache_status_optional(self):
        """Test /health endpoint cache status can be null."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            data = response.json()

            # Cache can be null (if not configured), or valid string
            if data["cache"] is not None:
                assert data["cache"] in ["ok", "error", "unknown"]

    @pytest.mark.asyncio
    async def test_health_check_healthy_status_code(self):
        """Test /health returns 200 when healthy."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")

            # Should return 200 for healthy or degraded
            assert response.status_code in [200, 503]

    @pytest.mark.asyncio
    async def test_readiness_check(self):
        """Test /ready endpoint returns correct response."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/ready")

            assert response.status_code == 200
            data = response.json()
            assert data["ready"] is True

    @pytest.mark.asyncio
    async def test_readiness_check_structure(self):
        """Test /ready endpoint response structure."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/ready")
            data = response.json()

            # Must have 'ready' field
            assert "ready" in data
            assert isinstance(data["ready"], bool)

    @pytest.mark.asyncio
    async def test_health_check_multiple_calls(self):
        """Test /health endpoint consistency across multiple calls."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response1 = await client.get("/health")
            response2 = await client.get("/health")

            data1 = response1.json()
            data2 = response2.json()

            # Version and environment should be consistent
            assert data1["version"] == data2["version"]
            assert data1["environment"] == data2["environment"]
            assert data1["database"] == data2["database"]

            # Uptime should increase
            assert data2["uptime_seconds"] >= data1["uptime_seconds"]

    @pytest.mark.asyncio
    async def test_health_check_in_swagger(self):
        """Test /health endpoint is documented in Swagger."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/openapi.json")
            spec = response.json()

            # Check that /health is in paths
            assert "/health" in spec["paths"]
            assert "get" in spec["paths"]["/health"]

    @pytest.mark.asyncio
    async def test_ready_check_in_swagger(self):
        """Test /ready endpoint is documented in Swagger."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/openapi.json")
            spec = response.json()

            # Check that /ready is in paths
            assert "/ready" in spec["paths"]
            assert "get" in spec["paths"]["/ready"]
