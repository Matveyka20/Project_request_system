"""FastAPI REST API for the request system."""

from typing import Callable

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from request_system.config import settings
from request_system.application.ports.persistence import UnitOfWork
from request_system.application.services.request_service import RequestService
from request_system.application.services.health_service import health_service
from request_system.presentation.models import (
    HealthCheckResponse,
    ListRequestsQueryParams,
    ListRequestsResponse,
    RequestItemResponse,
)


def create_app(unit_of_work_factory: Callable[[], UnitOfWork]) -> FastAPI:
    """Create and configure the FastAPI application with OpenAPI documentation."""
    app = FastAPI(
        title=settings.api_title,
        description="Production-grade REST API for managing support requests with advanced search, filtering, sorting, and pagination capabilities.",
        version=settings.api_version,
        docs_url=settings.api_docs_url,
        redoc_url=settings.api_redoc_url,
        openapi_url=settings.api_openapi_url,
    )

    service = RequestService(unit_of_work_factory)

    # =========================================================================
    # Health Check Endpoints
    # =========================================================================

    @app.get(
        "/health",
        response_model=HealthCheckResponse,
        tags=["Health"],
        summary="Comprehensive health check",
        description="Returns detailed health status of the API service including database, cache, and uptime information. Used by Docker, Kubernetes, and load balancers.",
        responses={
            200: {"description": "Application is healthy or degraded (services responding)"},
            503: {"description": "Application is unhealthy (critical services down)"}
        }
    )
    async def health_check() -> HealthCheckResponse:
        """
        Comprehensive health check endpoint.

        Returns detailed information about application status including:
        - Overall health status (healthy, degraded, unhealthy)
        - API version
        - Application uptime
        - Database status
        - Cache status (if configured)
        - Environment (development, production, staging)
        - Python version

        Response codes:
            200: Healthy or degraded (services responding)
            503: Unhealthy (critical services down)

        Used by:
            - Docker HEALTHCHECK
            - Kubernetes liveness/readiness probes
            - Load balancer health checks
            - Monitoring systems
        """
        health = await health_service.check_health(settings)
        status_code = 200 if health.status != "unhealthy" else 503
        return JSONResponse(content=health.model_dump(mode="json"), status_code=status_code)

    @app.get(
        "/ready",
        tags=["Health"],
        summary="Readiness check",
        description="Simple readiness check endpoint. Returns 200 if application is ready to accept requests.",
        status_code=200
    )
    async def readiness_check():
        """
        Simple readiness check endpoint.

        Returns:
            {"ready": true} if application is ready

        Used by:
            - Kubernetes readiness probes
            - Docker container orchestration
            - Simple health verification
        """
        return JSONResponse(
            status_code=200,
            content={"ready": True}
        )

    @app.get(
        "/api/requests",
        response_model=ListRequestsResponse,
        summary="Get list of requests with advanced filtering and search",
        description="Retrieve a paginated list of requests with comprehensive filtering, full-text search, sorting, and pagination capabilities.",
        tags=["Requests"],
        status_code=200,
    )
    async def list_requests(
        user_id: int | None = Query(
            None,
            ge=1,
            description="Filter by applicant user ID. Returns only requests created by this user. Example: 1"
        ),
        category_id: int | None = Query(
            None,
            ge=1,
            description="Filter by request category ID. Returns only requests in this category. Example: 2"
        ),
        status: str | None = Query(
            None,
            description="Filter by request status. Valid values: New, In Progress, Under Review, Approved, Rejected, Completed. Example: In Progress"
        ),
        priority: str | None = Query(
            None,
            description="Filter by priority level. Valid values: Low, Medium, High, Critical. Example: High"
        ),
        account_name: str | None = Query(
            None,
            min_length=1,
            max_length=255,
            description="Filter by account name (substring match, case-insensitive). Example: John"
        ),
        search: str | None = Query(
            None,
            min_length=1,
            max_length=500,
            description="Full-text search across description and account_name fields (case-insensitive). Example: laptop"
        ),
        search_description: str | None = Query(
            None,
            min_length=1,
            max_length=500,
            description="Search only in description field (case-insensitive). For precise description-only results. Example: equipment"
        ),
        sort_by: str = Query(
            "created_at",
            pattern="^(created_at|id|priority|status|account_name)$",
            description="Field to sort by. Options: created_at (chronological), id (natural), priority (level), status (alphabetical), account_name (user name). Default: created_at"
        ),
        sort_order: str = Query(
            "desc",
            pattern="^(asc|desc)$",
            description="Sort order direction. asc=ascending (oldest/lowest first), desc=descending (newest/highest first). Default: desc"
        ),
        limit: int = Query(
            10,
            ge=1,
            le=100,
            description="Maximum number of results per page. Default: 10, Range: 1-100. Recommended: 10-50 for optimal performance"
        ),
        offset: int | None = Query(
            0,
            ge=0,
            description="Number of results to skip (0-indexed). Default: 0. Use with limit for traditional offset-based pagination. Example: offset=20 with limit=10 returns items 21-30"
        ),
        page: int | None = Query(
            None,
            ge=1,
            description="Page number for page-based pagination (1-indexed, alternative to offset). If provided, overrides offset. Example: page=2 with limit=10 is equivalent to offset=10"
        ),
    ) -> ListRequestsResponse:
        """
        ## Get a paginated list of requests with advanced filtering, searching, sorting, and pagination.
        
        This endpoint provides comprehensive query capabilities for retrieving requests with various filtering options.
        
        ### **Key Features:**
        
        1. **Multi-Filter Support (AND Logic)**
           - Combine any number of filters to narrow results
           - Filters work together: all must match for a request to be included
           - Example: user_id=1 AND status=In Progress AND priority=High
        
        2. **Full-Text Search**
           - `search`: Searches across both description and account_name fields
           - `search_description`: Searches only in description field
           - Both are case-insensitive substring matches
        
        3. **Flexible Sorting**
           - Sort by 5 different fields
           - Choose ascending (oldest/lowest first) or descending (newest/highest first)
           - Default: sort by created_at descending (newest first)
        
        4. **Dual Pagination Modes**
           - **Offset-based**: Use limit + offset (traditional pagination)
           - **Page-based**: Use limit + page (1-indexed page numbers)
           - Page parameter overrides offset if both are provided
        
        ### **Usage Examples:**
        
        #### Example 1: Basic List
        ```
        GET /api/requests
        ```
        Returns all requests with defaults (limit=10, offset=0, sorted by created_at desc)
        
        #### Example 2: Filter by Status
        ```
        GET /api/requests?status=In%20Progress&limit=20
        ```
        Returns up to 20 in-progress requests
        
        #### Example 3: Full-Text Search
        ```
        GET /api/requests?search=laptop
        ```
        Searches for 'laptop' in description or account_name (case-insensitive)
        
        #### Example 4: Multiple Filters + Search + Sort
        ```
        GET /api/requests?user_id=1&status=In%20Progress&priority=High&sort_by=created_at&sort_order=desc&limit=10&offset=0
        ```
        Returns high-priority in-progress requests from user 1, sorted newest first
        
        #### Example 5: Pagination via Page Number
        ```
        GET /api/requests?limit=20&page=2
        ```
        Returns page 2 with 20 items per page (items 21-40)
        
        #### Example 6: Description-Only Search
        ```
        GET /api/requests?search_description=equipment
        ```
        Searches only in description field for 'equipment'
        
        #### Example 7: Account Name Filter
        ```
        GET /api/requests?account_name=john
        ```
        Returns requests from users with 'john' in their name (case-insensitive)
        
        ### **Filter Values:**
        
        **Status:** New | In Progress | Under Review | Approved | Rejected | Completed
        
        **Priority:** Low | Medium | High | Critical
        
        ### **Response Fields:**
        
        - `requests`: Array of request objects (empty if no results)
        - `total_count`: Total requests in database (ignoring all filters)
        - `filtered_count`: Requests matching all filters (before pagination)
        - `returned_count`: Requests actually in this response (≤ limit)
        - `limit`: Page size used
        - `offset`: Starting position used
        - `has_next`: Whether more results exist after this page
        - `has_previous`: Whether results exist before this page
        
        ### **Response Codes:**
        
        - **200 OK**: Successful response (returns results or empty array)
        - **400 Bad Request**: Invalid query parameters
        - **422 Unprocessable Entity**: Invalid enum values or parameter types
        
        ### **Performance Notes:**
        
        - Limit is capped at 100 to prevent excessive data transfer
        - For best performance, use specific filters instead of full-text search
        - Page sizes of 10-50 recommended for optimal performance
        - Sorting by indexed fields (created_at, id) is faster
        
        ### **Pagination Best Practices:**
        
        1. **For UI Pagination**: Use limit + page for better UX (1-indexed pages)
        2. **For Cursor Pagination**: Use limit + offset with has_next/has_previous
        3. **For Large Datasets**: Use lower limit (10-20) and check has_next before next request
        """
        calculate_offset = offset if offset is not None else 0
        if page is not None and page >= 1:
            calculate_offset = (page - 1) * limit

        result = service.list_requests_with_filters(
            user_id=user_id,
            category_id=category_id,
            status=status,
            priority=priority,
            account_name=account_name,
            search=search,
            search_description=search_description,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=calculate_offset,
        )

        request_items = [
            RequestItemResponse(
                request_id=req.request_id or 0,
                request_number=req.request_number,
                description=req.description,
                applicant_user_id=req.applicant_user_id,
                user_name=user_name,
                category_id=req.category_id,
                category_name=category_name,
                priority=req.priority,
                status=status_obj.name,
                registered_at=req.registered_at,
            )
            for req, status_obj, user_name, category_name in result.requests
        ]

        return ListRequestsResponse(
            requests=request_items,
            total_count=result.total_count,
            filtered_count=result.filtered_count,
            returned_count=result.returned_count,
            limit=result.limit,
            offset=result.offset,
            has_next=result.has_next,
            has_previous=result.has_previous,
        )

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return JSONResponse({"status": "ok"})

    return app
