# API Response Examples

Complete documentation of all 13 API test scenarios with curl commands and JSON responses.

---

## 1. Get All Requests (Basic)

**Description:** Retrieve all requests with default pagination (limit=10, offset=0)

**curl Command:**
```bash
curl -X GET "http://localhost:8000/api/requests" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "requests": [
    {
      "request_id": 1,
      "request_number": "REQ-20261115-001",
      "description": "Need new laptop for development",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "In Progress",
      "registered_at": "2026-11-15T18:00:00Z"
    },
    {
      "request_id": 2,
      "request_number": "REQ-20261115-002",
      "description": "Office furniture refurbishment",
      "applicant_user_id": 2,
      "user_name": "Jane Smith",
      "category_id": 2,
      "category_name": "Office",
      "priority": "Medium",
      "status": "New",
      "registered_at": "2026-11-15T18:15:00Z"
    },
    {
      "request_id": 3,
      "request_number": "REQ-20261115-003",
      "description": "Software license purchase",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "New",
      "registered_at": "2026-11-15T18:30:00Z"
    },
    {
      "request_id": 4,
      "request_number": "REQ-20261115-004",
      "description": "Meeting room equipment upgrade",
      "applicant_user_id": 3,
      "user_name": "Bob Johnson",
      "category_id": 2,
      "category_name": "Office",
      "priority": "Low",
      "status": "New",
      "registered_at": "2026-11-15T18:45:00Z"
    },
    {
      "request_id": 5,
      "request_number": "REQ-20261115-005",
      "description": "Network infrastructure upgrade needed",
      "applicant_user_id": 2,
      "user_name": "Jane Smith",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "Critical",
      "status": "In Progress",
      "registered_at": "2026-11-15T19:00:00Z"
    }
  ],
  "total_count": 5,
  "filtered_count": 5,
  "returned_count": 5,
  "limit": 10,
  "offset": 0,
  "has_next": false,
  "has_previous": false
}
```

---

## 2. Filter by User ID

**Description:** Get all requests created by user_id=1

**curl Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?user_id=1" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "requests": [
    {
      "request_id": 1,
      "request_number": "REQ-20261115-001",
      "description": "Need new laptop for development",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "In Progress",
      "registered_at": "2026-11-15T18:00:00Z"
    },
    {
      "request_id": 3,
      "request_number": "REQ-20261115-003",
      "description": "Software license purchase",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "New",
      "registered_at": "2026-11-15T18:30:00Z"
    }
  ],
  "total_count": 5,
  "filtered_count": 2,
  "returned_count": 2,
  "limit": 10,
  "offset": 0,
  "has_next": false,
  "has_previous": false
}
```

---

## 3. Filter by Status

**Description:** Get all requests with status="New"

**curl Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?status=New" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "requests": [
    {
      "request_id": 2,
      "request_number": "REQ-20261115-002",
      "description": "Office furniture refurbishment",
      "applicant_user_id": 2,
      "user_name": "Jane Smith",
      "category_id": 2,
      "category_name": "Office",
      "priority": "Medium",
      "status": "New",
      "registered_at": "2026-11-15T18:15:00Z"
    },
    {
      "request_id": 3,
      "request_number": "REQ-20261115-003",
      "description": "Software license purchase",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "New",
      "registered_at": "2026-11-15T18:30:00Z"
    },
    {
      "request_id": 4,
      "request_number": "REQ-20261115-004",
      "description": "Meeting room equipment upgrade",
      "applicant_user_id": 3,
      "user_name": "Bob Johnson",
      "category_id": 2,
      "category_name": "Office",
      "priority": "Low",
      "status": "New",
      "registered_at": "2026-11-15T18:45:00Z"
    }
  ],
  "total_count": 5,
  "filtered_count": 3,
  "returned_count": 3,
  "limit": 10,
  "offset": 0,
  "has_next": false,
  "has_previous": false
}
```

---

## 4. Filter by Priority

**Description:** Get all requests with priority="High"

**curl Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?priority=High" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "requests": [
    {
      "request_id": 1,
      "request_number": "REQ-20261115-001",
      "description": "Need new laptop for development",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "In Progress",
      "registered_at": "2026-11-15T18:00:00Z"
    },
    {
      "request_id": 3,
      "request_number": "REQ-20261115-003",
      "description": "Software license purchase",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "New",
      "registered_at": "2026-11-15T18:30:00Z"
    }
  ],
  "total_count": 5,
  "filtered_count": 2,
  "returned_count": 2,
  "limit": 10,
  "offset": 0,
  "has_next": false,
  "has_previous": false
}
```

---

## 5. Filter by Category ID

**Description:** Get all requests in category_id=1 (IT Equipment)

**curl Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?category_id=1" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "requests": [
    {
      "request_id": 1,
      "request_number": "REQ-20261115-001",
      "description": "Need new laptop for development",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "In Progress",
      "registered_at": "2026-11-15T18:00:00Z"
    },
    {
      "request_id": 3,
      "request_number": "REQ-20261115-003",
      "description": "Software license purchase",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "New",
      "registered_at": "2026-11-15T18:30:00Z"
    },
    {
      "request_id": 5,
      "request_number": "REQ-20261115-005",
      "description": "Network infrastructure upgrade needed",
      "applicant_user_id": 2,
      "user_name": "Jane Smith",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "Critical",
      "status": "In Progress",
      "registered_at": "2026-11-15T19:00:00Z"
    }
  ],
  "total_count": 5,
  "filtered_count": 3,
  "returned_count": 3,
  "limit": 10,
  "offset": 0,
  "has_next": false,
  "has_previous": false
}
```

---

## 6. Full-Text Search

**Description:** Full-text search for "laptop" across description and account_name fields

**curl Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?search=laptop" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "requests": [
    {
      "request_id": 1,
      "request_number": "REQ-20261115-001",
      "description": "Need new laptop for development",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "In Progress",
      "registered_at": "2026-11-15T18:00:00Z"
    }
  ],
  "total_count": 5,
  "filtered_count": 1,
  "returned_count": 1,
  "limit": 10,
  "offset": 0,
  "has_next": false,
  "has_previous": false
}
```

---

## 7. Search in Description Only

**Description:** Search for "equipment" only in description field

**curl Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?search_description=equipment" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "requests": [
    {
      "request_id": 4,
      "request_number": "REQ-20261115-004",
      "description": "Meeting room equipment upgrade",
      "applicant_user_id": 3,
      "user_name": "Bob Johnson",
      "category_id": 2,
      "category_name": "Office",
      "priority": "Low",
      "status": "New",
      "registered_at": "2026-11-15T18:45:00Z"
    },
    {
      "request_id": 5,
      "request_number": "REQ-20261115-005",
      "description": "Network infrastructure upgrade needed",
      "applicant_user_id": 2,
      "user_name": "Jane Smith",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "Critical",
      "status": "In Progress",
      "registered_at": "2026-11-15T19:00:00Z"
    }
  ],
  "total_count": 5,
  "filtered_count": 2,
  "returned_count": 2,
  "limit": 10,
  "offset": 0,
  "has_next": false,
  "has_previous": false
}
```

---

## 8. Sort by Priority (Descending)

**Description:** Sort all requests by priority in descending order (Critical → High → Medium → Low)

**curl Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?sort_by=priority&sort_order=desc" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "requests": [
    {
      "request_id": 5,
      "request_number": "REQ-20261115-005",
      "description": "Network infrastructure upgrade needed",
      "applicant_user_id": 2,
      "user_name": "Jane Smith",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "Critical",
      "status": "In Progress",
      "registered_at": "2026-11-15T19:00:00Z"
    },
    {
      "request_id": 1,
      "request_number": "REQ-20261115-001",
      "description": "Need new laptop for development",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "In Progress",
      "registered_at": "2026-11-15T18:00:00Z"
    },
    {
      "request_id": 3,
      "request_number": "REQ-20261115-003",
      "description": "Software license purchase",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "New",
      "registered_at": "2026-11-15T18:30:00Z"
    },
    {
      "request_id": 2,
      "request_number": "REQ-20261115-002",
      "description": "Office furniture refurbishment",
      "applicant_user_id": 2,
      "user_name": "Jane Smith",
      "category_id": 2,
      "category_name": "Office",
      "priority": "Medium",
      "status": "New",
      "registered_at": "2026-11-15T18:15:00Z"
    },
    {
      "request_id": 4,
      "request_number": "REQ-20261115-004",
      "description": "Meeting room equipment upgrade",
      "applicant_user_id": 3,
      "user_name": "Bob Johnson",
      "category_id": 2,
      "category_name": "Office",
      "priority": "Low",
      "status": "New",
      "registered_at": "2026-11-15T18:45:00Z"
    }
  ],
  "total_count": 5,
  "filtered_count": 5,
  "returned_count": 5,
  "limit": 10,
  "offset": 0,
  "has_next": false,
  "has_previous": false
}
```

---

## 9. Sort by ID (Ascending)

**Description:** Sort all requests by ID in ascending order (1 → 5)

**curl Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?sort_by=id&sort_order=asc" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "requests": [
    {
      "request_id": 1,
      "request_number": "REQ-20261115-001",
      "description": "Need new laptop for development",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "In Progress",
      "registered_at": "2026-11-15T18:00:00Z"
    },
    {
      "request_id": 2,
      "request_number": "REQ-20261115-002",
      "description": "Office furniture refurbishment",
      "applicant_user_id": 2,
      "user_name": "Jane Smith",
      "category_id": 2,
      "category_name": "Office",
      "priority": "Medium",
      "status": "New",
      "registered_at": "2026-11-15T18:15:00Z"
    },
    {
      "request_id": 3,
      "request_number": "REQ-20261115-003",
      "description": "Software license purchase",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "New",
      "registered_at": "2026-11-15T18:30:00Z"
    },
    {
      "request_id": 4,
      "request_number": "REQ-20261115-004",
      "description": "Meeting room equipment upgrade",
      "applicant_user_id": 3,
      "user_name": "Bob Johnson",
      "category_id": 2,
      "category_name": "Office",
      "priority": "Low",
      "status": "New",
      "registered_at": "2026-11-15T18:45:00Z"
    },
    {
      "request_id": 5,
      "request_number": "REQ-20261115-005",
      "description": "Network infrastructure upgrade needed",
      "applicant_user_id": 2,
      "user_name": "Jane Smith",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "Critical",
      "status": "In Progress",
      "registered_at": "2026-11-15T19:00:00Z"
    }
  ],
  "total_count": 5,
  "filtered_count": 5,
  "returned_count": 5,
  "limit": 10,
  "offset": 0,
  "has_next": false,
  "has_previous": false
}
```

---

## 10. Pagination with Limit and Offset

**Description:** Get first 2 requests using limit=2&offset=0

**curl Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?limit=2&offset=0" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "requests": [
    {
      "request_id": 1,
      "request_number": "REQ-20261115-001",
      "description": "Need new laptop for development",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "In Progress",
      "registered_at": "2026-11-15T18:00:00Z"
    },
    {
      "request_id": 2,
      "request_number": "REQ-20261115-002",
      "description": "Office furniture refurbishment",
      "applicant_user_id": 2,
      "user_name": "Jane Smith",
      "category_id": 2,
      "category_name": "Office",
      "priority": "Medium",
      "status": "New",
      "registered_at": "2026-11-15T18:15:00Z"
    }
  ],
  "total_count": 5,
  "filtered_count": 5,
  "returned_count": 2,
  "limit": 2,
  "offset": 0,
  "has_next": true,
  "has_previous": false
}
```

---

## 11. Pagination with Page Parameter

**Description:** Get page 2 with limit=2&page=2 (equivalent to offset=2)

**curl Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?limit=2&page=2" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "requests": [
    {
      "request_id": 3,
      "request_number": "REQ-20261115-003",
      "description": "Software license purchase",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "New",
      "registered_at": "2026-11-15T18:30:00Z"
    },
    {
      "request_id": 4,
      "request_number": "REQ-20261115-004",
      "description": "Meeting room equipment upgrade",
      "applicant_user_id": 3,
      "user_name": "Bob Johnson",
      "category_id": 2,
      "category_name": "Office",
      "priority": "Low",
      "status": "New",
      "registered_at": "2026-11-15T18:45:00Z"
    }
  ],
  "total_count": 5,
  "filtered_count": 5,
  "returned_count": 2,
  "limit": 2,
  "offset": 2,
  "has_next": true,
  "has_previous": true
}
```

---

## 12. Combined Filters, Search, Sort, and Pagination

**Description:** Complex query combining multiple filters with search, sorting and pagination

**curl Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?user_id=1&status=In%20Progress&search=software&sort_by=created_at&sort_order=desc&limit=10&offset=0" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "requests": [
    {
      "request_id": 1,
      "request_number": "REQ-20261115-001",
      "description": "Need new laptop for development",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "In Progress",
      "registered_at": "2026-11-15T18:00:00Z"
    }
  ],
  "total_count": 5,
  "filtered_count": 1,
  "returned_count": 1,
  "limit": 10,
  "offset": 0,
  "has_next": false,
  "has_previous": false
}
```

---

## 13. Filter by Account Name (Substring)

**Description:** Filter requests by account_name containing "Doe" (case-insensitive)

**curl Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?account_name=Doe" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "requests": [
    {
      "request_id": 1,
      "request_number": "REQ-20261115-001",
      "description": "Need new laptop for development",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "In Progress",
      "registered_at": "2026-11-15T18:00:00Z"
    },
    {
      "request_id": 3,
      "request_number": "REQ-20261115-003",
      "description": "Software license purchase",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT Equipment",
      "priority": "High",
      "status": "New",
      "registered_at": "2026-11-15T18:30:00Z"
    }
  ],
  "total_count": 5,
  "filtered_count": 2,
  "returned_count": 2,
  "limit": 10,
  "offset": 0,
  "has_next": false,
  "has_previous": false
}
```

---

## Response Format Reference

All responses follow this structure:

```json
{
  "requests": [
    {
      "request_id": integer,
      "request_number": string,
      "description": string,
      "applicant_user_id": integer,
      "user_name": string,
      "category_id": integer,
      "category_name": string,
      "priority": string,
      "status": string,
      "registered_at": string (ISO 8601 datetime)
    }
  ],
  "total_count": integer,
  "filtered_count": integer,
  "returned_count": integer,
  "limit": integer,
  "offset": integer,
  "has_next": boolean,
  "has_previous": boolean
}
```

### Field Descriptions

- **requests**: Array of request objects matching the query parameters
- **total_count**: Total number of requests in the database
- **filtered_count**: Number of requests after applying all filters and search terms
- **returned_count**: Number of requests actually returned in this response (may be less than filtered_count due to pagination)
- **limit**: Page size used for this request
- **offset**: Starting position in the filtered results
- **has_next**: True if there are more results beyond this page
- **has_previous**: True if there are results before this page

---

## Error Responses

### 400 Bad Request - Invalid Parameters

```bash
curl -X GET "http://localhost:8000/api/requests?limit=200" \
  -H "Content-Type: application/json"
```

```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["query", "limit"],
      "msg": "Input should be less than or equal to 100",
      "input": 200,
      "ctx": {"le": 100}
    }
  ]
}
```

### 400 Bad Request - Invalid Status

```bash
curl -X GET "http://localhost:8000/api/requests?status=Invalid" \
  -H "Content-Type: application/json"
```

```json
{
  "detail": [
    {
      "type": "enum",
      "loc": ["query", "status"],
      "msg": "Input should be 'New', 'In Progress', 'Under Review', 'Approved', 'Rejected', or 'Completed'",
      "input": "Invalid",
      "ctx": {"expected": "'New', 'In Progress', 'Under Review', 'Approved', 'Rejected', 'Completed'"}
    }
  ]
}
```

### 422 Unprocessable Entity - Invalid Priority

```bash
curl -X GET "http://localhost:8000/api/requests?priority=Unknown" \
  -H "Content-Type: application/json"
```

```json
{
  "detail": [
    {
      "type": "enum",
      "loc": ["query", "priority"],
      "msg": "Input should be 'Low', 'Medium', 'High', or 'Critical'",
      "input": "Unknown",
      "ctx": {"expected": "'Low', 'Medium', 'High', 'Critical'"}
    }
  ]
}
```

---

## Best Practices

1. **Use page parameter for page-based navigation**: Easier for UI pagination
2. **Use offset for cursor-based navigation**: Better for scrolling infinite lists
3. **Combine filters with AND logic**: Multiple filters narrow results further
4. **Use search for user-facing queries**: Full-text search provides better UX
5. **Sort by created_at for chronological ordering**: Default behavior most users expect
6. **Check has_next to determine if more results exist**: Prevents extra requests
7. **URL-encode special characters**: Spaces become %20, etc.

---

## Testing Checklist

- [ ] All requests return HTTP 200
- [ ] Filters reduce result count appropriately
- [ ] Search finds matching items
- [ ] Sorting changes result order correctly
- [ ] Pagination respects limit and offset
- [ ] has_next and has_previous are accurate
- [ ] Metadata counts are consistent
- [ ] Each request includes all required fields
