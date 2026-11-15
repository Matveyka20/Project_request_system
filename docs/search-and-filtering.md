# Search and Filtering API Documentation

## Overview

The Request Management System provides a powerful REST API for searching, filtering, sorting, and paginating through requests. The `GET /api/requests` endpoint supports comprehensive query parameters to help clients efficiently retrieve and analyze request data.

## Base URL

```
GET /api/requests
```

## Query Parameters

### Filtering Parameters

#### `user_id` (optional)
Filter requests by the applicant user ID.
- **Type:** integer
- **Example:** `GET /api/requests?user_id=1`

#### `category_id` (optional)
Filter requests by category ID.
- **Type:** integer
- **Example:** `GET /api/requests?category_id=2`

#### `status` (optional)
Filter requests by their current status name.
- **Type:** string
- **Valid values:** "Новая", "В работе", "Завершена" (or custom statuses configured in the system)
- **Example:** `GET /api/requests?status=В%20работе`
- **Note:** Status names should be URL-encoded if they contain spaces

#### `priority` (optional)
Filter requests by their priority level.
- **Type:** string
- **Valid values:** "Высокий", "Средний", "Низкий" (or custom priorities)
- **Example:** `GET /api/requests?priority=Высокий`

#### `account_name` (optional)
Filter requests by the applicant's account name (substring match, case-insensitive).
- **Type:** string
- **Behavior:** Performs a substring match; e.g., searching for "john" will match "john.doe"
- **Example:** `GET /api/requests?account_name=john`

### Search Parameters

#### `search` (optional)
Perform a full-text search across the request description and applicant's account name (case-insensitive).
- **Type:** string
- **Behavior:** Case-insensitive substring search
- **Example:** `GET /api/requests?search=договор`

#### `search_description` (optional)
Search only within the request description field (case-insensitive).
- **Type:** string
- **Behavior:** Case-insensitive substring search
- **Example:** `GET /api/requests?search_description=оборудование`

### Sorting Parameters

#### `sort_by` (optional, default: "created_at")
Field to sort results by.
- **Type:** string
- **Valid values:**
  - `created_at` - Sort by request registration date (default)
  - `id` - Sort by request ID
  - `priority` - Sort by priority level
  - `status` - Sort by status name
  - `account_name` - Sort by applicant account name
- **Example:** `GET /api/requests?sort_by=priority`

#### `sort_order` (optional, default: "desc")
Sort order direction.
- **Type:** string
- **Valid values:**
  - `asc` - Ascending order
  - `desc` - Descending order (default)
- **Example:** `GET /api/requests?sort_order=asc`

### Pagination Parameters

#### `limit` (optional, default: 10)
Number of results to return per page.
- **Type:** integer
- **Range:** 1-100
- **Default:** 10
- **Example:** `GET /api/requests?limit=20`

#### `offset` (optional, default: 0)
Number of results to skip (zero-based).
- **Type:** integer
- **Minimum:** 0
- **Default:** 0
- **Example:** `GET /api/requests?limit=10&offset=20`

#### `page` (optional)
Alternative pagination parameter using page number (1-based).
- **Type:** integer
- **Minimum:** 1
- **Behavior:** When set, this overrides the `offset` parameter. The offset is calculated as `(page - 1) * limit`
- **Example:** `GET /api/requests?limit=10&page=2`

## Response Format

### Success Response (200 OK)

```json
{
  "requests": [
    {
      "request_id": 1,
      "request_number": "REQ-ABC123DEF",
      "description": "Требуется новое оборудование для отдела IT",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 2,
      "category_name": "IT",
      "priority": "Высокий",
      "status": "В работе",
      "registered_at": "2026-11-15T18:00:00Z"
    }
  ],
  "total_count": 100,
  "filtered_count": 15,
  "returned_count": 1,
  "limit": 10,
  "offset": 0,
  "has_next": true,
  "has_previous": false
}
```

### Response Fields

- **requests:** Array of request objects matching the query filters
- **total_count:** Total number of requests in the entire database
- **filtered_count:** Number of requests matching the applied filters
- **returned_count:** Number of requests actually returned in this response
- **limit:** The limit value used for pagination
- **offset:** The offset value used for pagination
- **has_next:** Boolean indicating if there are more results after this page
- **has_previous:** Boolean indicating if there are results before this page

## Usage Examples

### Example 1: Get the first 10 requests by default
```bash
curl -X GET "http://localhost:8000/api/requests"
```

### Example 2: Filter requests by specific user
```bash
curl -X GET "http://localhost:8000/api/requests?user_id=1&limit=20"
```

### Example 3: Filter by status and priority
```bash
curl -X GET "http://localhost:8000/api/requests?status=В%20работе&priority=Высокий"
```

### Example 4: Full-text search for "договор"
```bash
curl -X GET "http://localhost:8000/api/requests?search=договор"
```

### Example 5: Search only in description for "оборудование"
```bash
curl -X GET "http://localhost:8000/api/requests?search_description=оборудование&limit=10"
```

### Example 6: Filter by account name (substring match)
```bash
curl -X GET "http://localhost:8000/api/requests?account_name=john"
```

### Example 7: Sort by priority in ascending order
```bash
curl -X GET "http://localhost:8000/api/requests?sort_by=priority&sort_order=asc&limit=20"
```

### Example 8: Pagination with offset
```bash
curl -X GET "http://localhost:8000/api/requests?limit=10&offset=20"
```

### Example 9: Pagination with page number
```bash
curl -X GET "http://localhost:8000/api/requests?limit=10&page=3"
```

### Example 10: Complex query with multiple filters, search, sorting, and pagination
```bash
curl -X GET "http://localhost:8000/api/requests?user_id=1&category_id=2&status=В%20работе&search=договор&sort_by=created_at&sort_order=desc&limit=10&offset=0"
```

### Example 11: Find high-priority IT requests about equipment
```bash
curl -X GET "http://localhost:8000/api/requests?category_id=1&priority=Высокий&search_description=оборудование&sort_by=priority&sort_order=desc"
```

### Example 12: Get all requests from a specific user, sorted by status
```bash
curl -X GET "http://localhost:8000/api/requests?user_id=1&sort_by=status&sort_order=asc&limit=50"
```

### Example 13: Search for "документ" and paginate
```bash
curl -X GET "http://localhost:8000/api/requests?search=документ&limit=5&page=1"
```

### Example 14: Find requests by account name (case-insensitive)
```bash
curl -X GET "http://localhost:8000/api/requests?account_name=jane.smith&limit=20"
```

### Example 15: Combine account name filter with description search
```bash
curl -X GET "http://localhost:8000/api/requests?account_name=bob&search_description=собеседование&limit=10"
```

## Search Behavior

### Full-Text Search (`search` parameter)
- Searches across both the request description and the applicant's account name
- Performs case-insensitive substring matching
- If "договор" is searched, it will match:
  - Descriptions containing "договор" (any case)
  - Account names containing "договор" (any case)

### Description-Only Search (`search_description` parameter)
- Searches only in the request description field
- Performs case-insensitive substring matching
- Does not search in account names or other fields

## Filtering Behavior

### Combining Filters
All filters are combined with AND logic:
- `?user_id=1&category_id=2` returns only requests from user 1 AND in category 2
- Adding more filters further narrows the results

### Account Name Filter
- Performs case-insensitive substring matching
- Searching for "john" matches "john.doe", "John.Doe", "JOHN.DOE", etc.

### Status and Priority Filters
- Require exact matches (after case-insensitive comparison for account_name)
- Must match the exact status or priority name configured in the system

## Sorting Behavior

### Sort by Field
- `created_at`: Sorts by request registration timestamp
- `id`: Sorts by numeric request ID
- `priority`: Sorts by priority level (string sort)
- `status`: Sorts by status name (string sort)
- `account_name`: Sorts by applicant account name (case-insensitive)

### Sort Order
- `asc`: Ascending order (A-Z, earliest to latest)
- `desc`: Descending order (Z-A, latest to earliest) - default

## Pagination Behavior

### Using `limit` and `offset`
- `limit`: Number of items per page (1-100, default 10)
- `offset`: Number of items to skip from the beginning (default 0)
- Examples:
  - `limit=10&offset=0` - First 10 items
  - `limit=10&offset=10` - Items 11-20
  - `limit=10&offset=20` - Items 21-30

### Using `limit` and `page`
- `page`: Page number (1-based, so page 1 is the first page)
- Internally converted to: `offset = (page - 1) * limit`
- Examples:
  - `limit=10&page=1` - First 10 items (offset=0)
  - `limit=10&page=2` - Items 11-20 (offset=10)
  - `limit=10&page=3` - Items 21-30 (offset=20)

### Navigation with Metadata
Use `has_next` and `has_previous` flags to navigate:
```python
# Python example
if response['has_next']:
    next_page = current_page + 1
else:
    print("No more results")

if response['has_previous']:
    prev_page = current_page - 1
else:
    print("Already on first page")
```

## Error Handling

### Invalid Query Parameters
- Invalid integer values: Returns 422 Unprocessable Entity
- Invalid sort_by value: Falls back to default sort field
- Invalid sort_order value: Falls back to "desc"
- `limit` outside 1-100 range: Returns 422 Unprocessable Entity
- `offset` or `page` negative: Returns 422 Unprocessable Entity

### Empty Results
- No error is raised; the response will have:
  - `requests`: Empty array `[]`
  - `filtered_count`: 0
  - `returned_count`: 0
  - `has_next`: false
  - `has_previous`: false

## Performance Considerations

- The API performs in-memory filtering and sorting after fetching all requests
- For production use with large datasets, consider optimizing the persistence layer
- Pagination should be used to limit returned data size
- Search operations are linear (O(n)); consider adding database indices for full-text search

## Best Practices

1. **Use pagination for large datasets:** Always specify a `limit` to avoid overwhelming responses
2. **Narrow results with filters:** Combine multiple filters to quickly reach your target data
3. **Choose appropriate sort fields:** Sort by relevant fields to improve data usability
4. **Cache search results:** If performing the same query repeatedly, consider client-side caching
5. **Use page-based pagination:** For user-facing interfaces, page-based pagination is more intuitive
6. **Use offset-based pagination:** For API integrations and bulk data processing, offset-based is more flexible

## Status Codes

- **200 OK:** Successful request, results returned
- **422 Unprocessable Entity:** Invalid query parameters
- **500 Internal Server Error:** Server-side error during processing
