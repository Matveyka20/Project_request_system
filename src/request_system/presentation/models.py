"""Pydantic models for REST API request/response validation."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ListRequestsQueryParams(BaseModel):
    """Query parameters for GET /api/requests endpoint with filtering, searching, sorting, and pagination."""

    user_id: int | None = Field(
        None,
        ge=1,
        description="Filter by applicant user ID. Returns only requests created by this user. Example: user_id=1"
    )
    category_id: int | None = Field(
        None,
        ge=1,
        description="Filter by request category ID. Returns only requests in this category. Example: category_id=2"
    )
    status: str | None = Field(
        None,
        description="Filter by request status. Valid values: New, In Progress, Under Review, Approved, Rejected, Completed. Example: status=In%20Progress"
    )
    priority: str | None = Field(
        None,
        description="Filter by priority level. Valid values: Low, Medium, High, Critical. Example: priority=High"
    )
    account_name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Filter by account name using substring matching (case-insensitive). Example: account_name=John matches John Doe, john, etc."
    )

    search: str | None = Field(
        None,
        min_length=1,
        max_length=500,
        description="Full-text search across description and account_name fields (case-insensitive). Searches both fields for the term. Example: search=laptop"
    )
    search_description: str | None = Field(
        None,
        min_length=1,
        max_length=500,
        description="Search only in the description field (case-insensitive). Use this for precise description-only searches. Example: search_description=equipment"
    )

    sort_by: Literal["created_at", "id", "priority", "status", "account_name"] = Field(
        "created_at",
        description="Field to sort results by. Default: created_at (newest first). Valid values: created_at (timestamp), id (natural order), priority (critical to low), status (alphabetical), account_name (user name alphabetical)"
    )
    sort_order: Literal["asc", "desc"] = Field(
        "desc",
        description="Sort order direction. Default: desc (descending). Values: asc (ascending, oldest/lowest first), desc (descending, newest/highest first)"
    )

    limit: int = Field(
        10,
        ge=1,
        le=100,
        description="Maximum number of results to return per page. Default: 10. Range: 1-100. Use lower values (5-20) for better performance."
    )
    offset: int | None = Field(
        0,
        ge=0,
        description="Number of results to skip from the beginning (for offset-based pagination). Default: 0. Example: offset=20 with limit=10 returns items 21-30. Use with limit for traditional pagination."
    )
    page: int | None = Field(
        None,
        ge=1,
        description="Page number for page-based pagination (alternative to offset). Starts from 1. If provided, overrides offset (calculated as offset=(page-1)*limit). Example: page=2 with limit=10 is equivalent to offset=10"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "category_id": 2,
                "status": "В работе",
                "priority": "Высокий",
                "search": "договор",
                "sort_by": "created_at",
                "sort_order": "desc",
                "limit": 10,
                "offset": 0,
            }
        }


class RequestItemResponse(BaseModel):
    """Single request item in the API response."""

    request_id: int = Field(..., description="Unique identifier for the request. Auto-incremented primary key.")
    request_number: str = Field(..., description="Human-readable request number in format REQ-XXXXXXXX for easy reference and tracking.")
    description: str = Field(..., description="Detailed description of the request (10-2000 characters). Contains the main information about what is being requested.")
    applicant_user_id: int = Field(..., description="User ID of the person who created/submitted the request.")
    user_name: str = Field(..., description="Full name of the applicant user. Usually in format 'First Last' (e.g., 'John Doe').")
    category_id: int | None = Field(..., description="ID of the request category (e.g., 1=IT, 2=Office, 3=HR). Links to Categories table.")
    category_name: str = Field(..., description="Human-readable name of the request category (e.g., 'IT Equipment', 'Office Supplies').")
    priority: str | None = Field(..., description="Priority level of the request. Valid values: Low, Medium, High, Critical. Critical requests require urgent attention.")
    status: str = Field(..., description="Current status of the request. Valid values: New (just created), In Progress (being worked on), Under Review (pending approval), Approved (approved), Rejected (declined), Completed (finished).")
    registered_at: datetime = Field(..., description="ISO 8601 timestamp when the request was created in UTC timezone. Format: YYYY-MM-DDTHH:MM:SSZ")

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": 1,
                "request_number": "REQ-ABC123",
                "description": "Требуется новое оборудование для отдела IT",
                "applicant_user_id": 1,
                "user_name": "John Doe",
                "category_id": 2,
                "category_name": "IT",
                "priority": "Высокий",
                "status": "В работе",
                "registered_at": "2026-11-15T18:00:00Z",
            }
        }


class ListRequestsResponse(BaseModel):
    """Response for GET /api/requests endpoint with paginated list of requests and metadata."""

    requests: list[RequestItemResponse] = Field(
        ...,
        description="Array of request items matching the applied filters, searches, and sorting. Empty array if no results found."
    )
    total_count: int = Field(
        ...,
        description="Total number of requests in the database (without any filters applied). Useful for calculating total pages."
    )
    filtered_count: int = Field(
        ...,
        description="Number of requests matching all applied filters and search terms (before pagination). Shows how many results the query found."
    )
    returned_count: int = Field(
        ...,
        description="Number of requests actually returned in this response (after pagination). Will be ≤ limit and ≤ filtered_count."
    )
    limit: int = Field(
        ...,
        description="Page size used for this request (1-100). The maximum number of items per page."
    )
    offset: int = Field(
        ...,
        description="Starting position (0-indexed) used for this request. Shows which item number we started from."
    )
    has_next: bool = Field(
        ...,
        description="True if there are more results beyond this page. Use this to show 'Next' button in UI. Calculated as: (offset + limit) < filtered_count"
    )
    has_previous: bool = Field(
        ...,
        description="True if there are results before this page. Use this to show 'Previous' button in UI. Calculated as: offset > 0"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "requests": [
                    {
                        "request_id": 1,
                        "request_number": "REQ-ABC123",
                        "description": "Требуется новое оборудование",
                        "applicant_user_id": 1,
                        "user_name": "John Doe",
                        "category_id": 2,
                        "category_name": "IT",
                        "priority": "Высокий",
                        "status": "В работе",
                        "registered_at": "2026-11-15T18:00:00Z",
                    }
                ],
                "total_count": 100,
                "filtered_count": 15,
                "returned_count": 1,
                "limit": 10,
                "offset": 0,
                "has_next": True,
                "has_previous": False,
            }
        }
