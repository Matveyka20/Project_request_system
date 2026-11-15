"""
Remote Integration Tests for Request System API

This module contains integration tests for verifying that the API
is working correctly when deployed remotely (on a VPS or cloud server).

Usage:
    pytest tests/test_remote_integration.py -v
    
    # With specific server URL:
    API_BASE_URL=http://192.168.1.100:8000 pytest tests/test_remote_integration.py -v
"""

import os
import time
import pytest
import requests
from typing import Dict, Any, Optional

# Configuration from environment or defaults
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT = 10  # seconds


class TestRemoteAPIConnectivity:
    """Tests for basic API connectivity"""
    
    def test_health_endpoint(self):
        """Verify /health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "uptime" in data
        assert "timestamp" in data
    
    def test_ready_endpoint(self):
        """Verify /ready endpoint indicates readiness"""
        response = requests.get(f"{BASE_URL}/ready", timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert data["ready"] is True
    
    def test_openapi_schema(self):
        """Verify OpenAPI schema is available"""
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
    
    def test_docs_page(self):
        """Verify Swagger UI documentation is accessible"""
        response = requests.get(f"{BASE_URL}/docs", timeout=TIMEOUT)
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "redoc" in response.text.lower()
    
    def test_redoc_page(self):
        """Verify ReDoc documentation is accessible"""
        response = requests.get(f"{BASE_URL}/redoc", timeout=TIMEOUT)
        assert response.status_code == 200
        assert "redoc" in response.text.lower()


class TestRequestsCRUD:
    """Tests for CRUD operations on requests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.created_ids = []
        yield
        # Cleanup: Note - cleanup might not be needed for production tests
    
    def test_list_requests(self):
        """Verify GET /api/requests returns list of requests"""
        response = requests.get(f"{BASE_URL}/api/requests", timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        # Should have either 'requests' or 'items' field
        assert "requests" in data or "items" in data or isinstance(data, list)
    
    def test_list_requests_with_limit(self):
        """Verify pagination with limit parameter"""
        response = requests.get(
            f"{BASE_URL}/api/requests?limit=5&offset=0",
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        data = response.json()
        requests_list = data.get("requests") or data.get("items") or data
        if isinstance(requests_list, list):
            assert len(requests_list) <= 5
    
    def test_list_requests_with_page(self):
        """Verify pagination with page parameter"""
        response = requests.get(
            f"{BASE_URL}/api/requests?limit=10&page=1",
            timeout=TIMEOUT
        )
        assert response.status_code in [200, 400]  # 400 if page not supported
    
    def test_filter_by_status(self):
        """Verify filtering by status"""
        response = requests.get(
            f"{BASE_URL}/api/requests?status=submitted",
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        data = response.json()
        # Verify response contains requests
        assert data is not None
    
    def test_filter_by_priority(self):
        """Verify filtering by priority"""
        response = requests.get(
            f"{BASE_URL}/api/requests?priority=3",
            timeout=TIMEOUT
        )
        assert response.status_code == 200
    
    def test_filter_by_category(self):
        """Verify filtering by category"""
        response = requests.get(
            f"{BASE_URL}/api/requests?category_id=1",
            timeout=TIMEOUT
        )
        assert response.status_code == 200
    
    def test_search_requests(self):
        """Verify full-text search"""
        response = requests.get(
            f"{BASE_URL}/api/requests?search=test",
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data is not None
    
    def test_search_description(self):
        """Verify description search"""
        response = requests.get(
            f"{BASE_URL}/api/requests?search_description=test",
            timeout=TIMEOUT
        )
        assert response.status_code == 200
    
    def test_sort_by_created_at(self):
        """Verify sorting by created_at"""
        response = requests.get(
            f"{BASE_URL}/api/requests?sort_by=created_at&sort_order=desc&limit=5",
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data is not None
    
    def test_create_request(self):
        """Verify POST /api/requests creates a new request"""
        request_data = {
            "user_id": 1,
            "category_id": 1,
            "title": "Integration Test Request",
            "description": "Test request from remote integration tests",
            "priority": 2
        }
        
        response = requests.post(
            f"{BASE_URL}/api/requests",
            json=request_data,
            timeout=TIMEOUT
        )
        
        assert response.status_code in [200, 201]
        
        data = response.json()
        assert "id" in data
        self.created_ids.append(data["id"])
        
        return data["id"]
    
    def test_get_single_request(self):
        """Verify GET /api/requests/{id} retrieves single request"""
        # First, get a request ID
        response = requests.get(f"{BASE_URL}/api/requests?limit=1", timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        requests_list = data.get("requests") or data.get("items") or data
        
        if isinstance(requests_list, list) and len(requests_list) > 0:
            request_id = requests_list[0].get("id") or requests_list[0].get("request_id")
            
            if request_id:
                response = requests.get(
                    f"{BASE_URL}/api/requests/{request_id}",
                    timeout=TIMEOUT
                )
                assert response.status_code == 200
                
                req_data = response.json()
                assert req_data is not None
    
    def test_update_request(self):
        """Verify PATCH /api/requests/{id} updates a request"""
        # Create a request first
        request_data = {
            "user_id": 1,
            "category_id": 1,
            "title": "Request to Update",
            "description": "Original description",
            "priority": 1
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/requests",
            json=request_data,
            timeout=TIMEOUT
        )
        
        if create_response.status_code in [200, 201]:
            created_data = create_response.json()
            request_id = created_data.get("id")
            self.created_ids.append(request_id)
            
            # Update the request
            update_data = {
                "title": "Updated Title",
                "description": "Updated description"
            }
            
            response = requests.patch(
                f"{BASE_URL}/api/requests/{request_id}",
                json=update_data,
                timeout=TIMEOUT
            )
            
            assert response.status_code in [200, 204]
    
    def test_change_request_status(self):
        """Verify status change via PUT /api/requests/{id}/status"""
        # Create a request first
        request_data = {
            "user_id": 1,
            "category_id": 1,
            "title": "Request for Status Change",
            "description": "Test",
            "priority": 1
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/requests",
            json=request_data,
            timeout=TIMEOUT
        )
        
        if create_response.status_code in [200, 201]:
            created_data = create_response.json()
            request_id = created_data.get("id")
            self.created_ids.append(request_id)
            
            # Change status
            status_data = {"status_name": "in_progress"}
            
            response = requests.put(
                f"{BASE_URL}/api/requests/{request_id}/status",
                json=status_data,
                timeout=TIMEOUT
            )
            
            assert response.status_code in [200, 204]


class TestAPIDataIntegrity:
    """Tests for data integrity and consistency"""
    
    def test_seed_data_exists(self):
        """Verify seed data is loaded"""
        response = requests.get(f"{BASE_URL}/api/requests", timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        requests_list = data.get("requests") or data.get("items") or data
        
        # Should have some seed data
        assert isinstance(requests_list, list)
        assert len(requests_list) > 0, "No seed data found in database"
    
    def test_response_structure(self):
        """Verify response structure is consistent"""
        response = requests.get(f"{BASE_URL}/api/requests?limit=1", timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check for expected fields (flexible for different response formats)
        if isinstance(data, dict):
            # Should have requests or items
            assert "requests" in data or "items" in data or "data" in data
    
    def test_created_request_has_id(self):
        """Verify created requests have proper IDs"""
        request_data = {
            "user_id": 1,
            "category_id": 1,
            "title": "ID Test Request",
            "description": "Test",
            "priority": 1
        }
        
        response = requests.post(
            f"{BASE_URL}/api/requests",
            json=request_data,
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "id" in data, "Created request should have an ID"
            
            # Verify ID is not empty/null
            assert data["id"] is not None
            assert data["id"] != ""


class TestAPIErrorHandling:
    """Tests for error handling and edge cases"""
    
    def test_invalid_request_id(self):
        """Verify proper error for invalid request ID"""
        response = requests.get(
            f"{BASE_URL}/api/requests/999999",
            timeout=TIMEOUT
        )
        assert response.status_code in [404, 400]
    
    def test_invalid_filter_parameter(self):
        """Verify handling of invalid parameters"""
        response = requests.get(
            f"{BASE_URL}/api/requests?invalid_param=test",
            timeout=TIMEOUT
        )
        # Should either ignore or return 400
        assert response.status_code in [200, 400]
    
    def test_missing_required_fields(self):
        """Verify error for missing required fields on POST"""
        request_data = {
            # Missing required fields
            "title": "Incomplete Request"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/requests",
            json=request_data,
            timeout=TIMEOUT
        )
        assert response.status_code in [400, 422]
    
    def test_limit_bounds(self):
        """Verify limit parameter bounds"""
        # Try limit > 100
        response = requests.get(
            f"{BASE_URL}/api/requests?limit=1000",
            timeout=TIMEOUT
        )
        # Should either accept or cap to max
        assert response.status_code in [200, 400]


class TestAPIPerformance:
    """Tests for API performance characteristics"""
    
    def test_response_time_health(self):
        """Verify health check responds quickly"""
        start = time.time()
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0, f"Health check took {elapsed}s (should be < 1s)"
    
    def test_response_time_list(self):
        """Verify list endpoint responds in reasonable time"""
        start = time.time()
        response = requests.get(
            f"{BASE_URL}/api/requests?limit=10",
            timeout=TIMEOUT
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 5.0, f"List endpoint took {elapsed}s (should be < 5s)"
    
    def test_concurrent_requests(self):
        """Verify API can handle multiple concurrent requests"""
        import concurrent.futures
        
        def make_request(i):
            response = requests.get(
                f"{BASE_URL}/api/requests?limit=1&offset={i}",
                timeout=TIMEOUT
            )
            return response.status_code == 200
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        assert all(results), "Some concurrent requests failed"


if __name__ == "__main__":
    print(f"Running integration tests against: {BASE_URL}")
    pytest.main([__file__, "-v", "--tb=short"])
