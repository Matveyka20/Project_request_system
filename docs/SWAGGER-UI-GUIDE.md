# Swagger UI Guide - Request Management System API

## 📖 Quick Start

### **Access Swagger UI Locally**

1. **Start the API server:**
   ```bash
   cd <project_root>
   python -m uvicorn src.request_system.presentation.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Open in browser:**
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc (Alternative)**: http://localhost:8000/redoc
   - **Raw OpenAPI JSON**: http://localhost:8000/openapi.json

### **Production Access**

Once deployed, Swagger UI is available at:
- `https://api.yourdomain.com/docs` (Swagger UI)
- `https://api.yourdomain.com/redoc` (ReDoc UI)
- `https://api.yourdomain.com/openapi.json` (OpenAPI specification)

---

## 🎯 Swagger UI Features

### **1. Interactive API Testing ("Try It Out")**

Swagger UI allows you to test API endpoints directly without external tools like Postman or curl.

#### **How to Test an Endpoint:**

1. Find the endpoint in the API documentation (e.g., `GET /api/requests`)
2. Click the endpoint to expand its details
3. Click the **"Try it out"** button
4. Fill in the required/optional parameters:
   - Query parameters appear as form fields
   - Enter values for filters, search terms, pagination, etc.
5. Click **"Execute"** to send the request
6. View the response:
   - **Status Code** (e.g., 200 OK)
   - **Response Headers**
   - **Response Body** (formatted JSON)
7. Copy the **curl command** shown to use in scripts

#### **Example: Filter Requests by Status**

```
1. Expand "GET /api/requests"
2. Click "Try it out"
3. Set parameters:
   - status: "In Progress"
   - limit: 10
   - sort_order: "desc"
4. Click "Execute"
5. See 200 OK response with filtered results
```

### **2. Parameter Descriptions**

Each parameter includes:
- **Name** and **Type** (string, integer, etc.)
- **Required/Optional** indicator
- **Description** with details and examples
- **Valid Values** for enums (status, priority, sort_by, sort_order)
- **Constraints** (min/max for numbers, min/max length for strings)

#### **Example Parameters for GET /api/requests:**

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `user_id` | integer | No | Filter by user ID | `1` |
| `status` | string | No | Filter by status | `In Progress` |
| `priority` | string | No | Filter by priority | `High` |
| `search` | string | No | Full-text search | `laptop` |
| `sort_by` | string | No | Sort field (default: created_at) | `priority` |
| `sort_order` | string | No | Sort direction (default: desc) | `asc` |
| `limit` | integer | No | Results per page (default: 10, max: 100) | `20` |
| `offset` | integer | No | Skip results (default: 0) | `10` |
| `page` | integer | No | Page number (alternative to offset) | `2` |

### **3. Response Schema Inspection**

Click on response model names to see their structure:

```
Response Schema
↓
ListRequestsResponse
├── requests: array[RequestItemResponse]
│   └── Each item contains:
│       ├── request_id: integer
│       ├── request_number: string
│       ├── description: string
│       ├── applicant_user_id: integer
│       ├── user_name: string
│       ├── category_id: integer
│       ├── category_name: string
│       ├── priority: string
│       ├── status: string
│       └── registered_at: datetime
├── total_count: integer
├── filtered_count: integer
├── returned_count: integer
├── limit: integer
├── offset: integer
├── has_next: boolean
└── has_previous: boolean
```

### **4. Example Request/Response**

Swagger shows example values for:
- **Request**: Pre-filled parameter values (e.g., limit=10, offset=0)
- **Response**: Sample JSON response with actual data structure

This helps understand the expected format before making requests.

---

## 🔧 Common Use Cases

### **Use Case 1: List All Requests (Basic)**

**Goal**: Get first 10 requests, newest first

**Steps:**
1. Open http://localhost:8000/docs
2. Find `GET /api/requests`
3. Click "Try it out"
4. Leave all fields empty (defaults will be used)
5. Click "Execute"
6. See response with status 200 OK

**Expected Response:**
```json
{
  "requests": [
    {
      "request_id": 1,
      "request_number": "REQ-ABC123...",
      "description": "Need laptop",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT",
      "priority": "High",
      "status": "In Progress",
      "registered_at": "2026-11-15T18:00:00Z"
    }
  ],
  "total_count": 100,
  "filtered_count": 100,
  "returned_count": 1,
  "limit": 10,
  "offset": 0,
  "has_next": true,
  "has_previous": false
}
```

### **Use Case 2: Filter Requests by Status and Priority**

**Goal**: Find high-priority in-progress requests

**Steps:**
1. Expand `GET /api/requests`
2. Click "Try it out"
3. Set parameters:
   ```
   status: In Progress
   priority: High
   limit: 20
   sort_order: desc
   ```
4. Click "Execute"
5. View filtered results

**curl Equivalent:**
```bash
curl -X GET "http://localhost:8000/api/requests?status=In%20Progress&priority=High&limit=20&sort_order=desc"
```

### **Use Case 3: Search Requests**

**Goal**: Find all requests mentioning "laptop"

**Steps:**
1. Expand `GET /api/requests`
2. Click "Try it out"
3. Set parameters:
   ```
   search: laptop
   limit: 50
   ```
4. Click "Execute"
5. See all requests with "laptop" in description or account_name

**curl Equivalent:**
```bash
curl -X GET "http://localhost:8000/api/requests?search=laptop&limit=50"
```

### **Use Case 4: Sorted and Paginated Results**

**Goal**: Get page 2 of high-priority requests, sorted by priority descending

**Steps:**
1. Expand `GET /api/requests`
2. Click "Try it out"
3. Set parameters:
   ```
   priority: High
   sort_by: priority
   sort_order: desc
   limit: 20
   page: 2
   ```
4. Click "Execute"
5. See page 2 with 20 items

**curl Equivalent:**
```bash
curl -X GET "http://localhost:8000/api/requests?priority=High&sort_by=priority&sort_order=desc&limit=20&page=2"
```

### **Use Case 5: Complex Query (Multiple Filters + Search)**

**Goal**: Find high-priority in-progress requests for user 1, containing "equipment"

**Steps:**
1. Expand `GET /api/requests`
2. Click "Try it out"
3. Set parameters:
   ```
   user_id: 1
   status: In Progress
   priority: High
   search_description: equipment
   sort_by: created_at
   sort_order: desc
   limit: 10
   offset: 0
   ```
4. Click "Execute"
5. See filtered and sorted results

**curl Equivalent:**
```bash
curl -X GET "http://localhost:8000/api/requests?user_id=1&status=In%20Progress&priority=High&search_description=equipment&sort_by=created_at&sort_order=desc&limit=10&offset=0"
```

---

## 📊 Response Fields Explained

### **Pagination Metadata**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `total_count` | integer | Total requests in DB (no filters) | `100` |
| `filtered_count` | integer | Requests matching filters | `15` |
| `returned_count` | integer | Requests in this response | `10` |
| `limit` | integer | Max items per page | `10` |
| `offset` | integer | Skip count from start | `0` |
| `has_next` | boolean | More results after this page? | `true` |
| `has_previous` | boolean | Results before this page? | `false` |

### **Using Pagination Metadata in UI**

```javascript
// Example: React component using pagination

function RequestList({ data }) {
  return (
    <div>
      {/* Show results */}
      <ul>
        {data.requests.map(r => <li key={r.request_id}>{r.description}</li>)}
      </ul>
      
      {/* Show pagination info */}
      <p>
        Showing {data.returned_count} of {data.filtered_count} results
      </p>
      
      {/* Show navigation buttons */}
      <button disabled={!data.has_previous}>← Previous</button>
      <button disabled={!data.has_next}>Next →</button>
    </div>
  );
}
```

---

## 🔍 Advanced Features

### **1. Schema Validation**

Swagger validates your input before sending:
- ✅ **Type validation**: Must provide correct type (int, string, etc.)
- ✅ **Enum validation**: Status/Priority must be valid values
- ✅ **Range validation**: Limit must be 1-100, offset ≥ 0
- ✅ **Pattern validation**: Sort_order must be "asc" or "desc"

Invalid input shows error: `422 Unprocessable Entity`

### **2. Model Examples**

Each response model shows an example:
- Click on model name to see structure
- Example shows typical values for each field
- Helps understand response format

### **3. curl Command Generation**

When you execute a request:
1. Swagger generates the curl command
2. Copy it to use in scripts/CI/CD
3. Useful for documentation and automation

Example generated curl:
```bash
curl -X GET "http://localhost:8000/api/requests?user_id=1&status=In%20Progress&limit=20" \
  -H "accept: application/json"
```

### **4. Request/Response Headers**

Swagger shows:
- **Request Headers**: What headers were sent (e.g., Content-Type)
- **Response Headers**: Server response metadata
- Useful for debugging header-related issues

---

## 🐛 Troubleshooting

### **Problem: Swagger UI not loading**

**Solution:**
- Check if server is running: `python -m uvicorn src.request_system.presentation.main:app --reload`
- Verify port 8000 is accessible
- Try http://localhost:8000/docs (not https)
- Clear browser cache (Ctrl+Shift+Delete)

### **Problem: Parameters not showing**

**Solution:**
- Refresh the page (F5)
- Check that endpoint decorator has `Query()` parameters
- Verify parameter names match exactly

### **Problem: "422 Unprocessable Entity"**

**Solution:**
- Check parameter types (string vs integer)
- Verify enum values match exactly (case-sensitive)
- Check ranges (e.g., limit 1-100, offset ≥ 0)
- See error message for details

### **Problem: Empty responses**

**Solution:**
- This is normal! It means filters returned no matches
- Check that filter values are correct
- Try removing filters to see all data
- Use search instead to verify data exists

### **Problem: Slow responses**

**Solution:**
- Reduce limit (use 10-20 instead of 100)
- Add filters to narrow results
- Avoid complex full-text searches
- Use sort_by on indexed fields (created_at, id)

---

## 📚 Related Documentation

- **API Reference**: `docs/search-and-filtering.md` - Detailed endpoint documentation
- **Response Examples**: `docs/api-response-examples.md` - Real example responses for all scenarios
- **Testing Guide**: `docs/API-TESTING-GUIDE.md` - QA testing procedures
- **Postman Collection**: `docs/postman-collection.json` - Importable Postman collection
- **OpenAPI Spec**: `docs/openapi.yaml` - Machine-readable OpenAPI 3.0 specification

---

## 🚀 Best Practices

1. **Start Simple**
   - Test basic requests first (no filters)
   - Add complexity gradually (one filter at a time)
   - Verify each step before moving to next

2. **Use Descriptive Parameters**
   - Always add status/priority filters when possible
   - Use search_description for description-only searches
   - Use search for broader full-text searches

3. **Optimize Pagination**
   - Use page-based pagination (limit + page) for UI
   - Use offset-based pagination (limit + offset) for API-to-API
   - Always check has_next/has_previous before requesting next page

4. **Handle Errors**
   - 422 errors: Check parameter types and valid values
   - 400 errors: Check parameter names and syntax
   - 200 OK with empty array: Normal, means no results match filters

5. **Performance**
   - Use limit 10-20 for optimal performance
   - Avoid very long search terms
   - Sort by indexed fields when possible
   - Apply filters before search for better results

---

## ✅ Testing Checklist

After deploying API, verify:

- [ ] Swagger UI loads at /docs
- [ ] ReDoc loads at /redoc
- [ ] OpenAPI JSON available at /openapi.json
- [ ] All 11 query parameters show with descriptions
- [ ] Response models display correctly
- [ ] "Try it out" button works
- [ ] Can execute requests and see responses
- [ ] Example values show in request/response
- [ ] Status codes (200) correct
- [ ] Error responses (422, 400) show details

---

## 📞 Support

For issues with:
- **API functionality**: Check `docs/search-and-filtering.md`
- **Testing**: Check `docs/API-TESTING-GUIDE.md`
- **Integration**: See `docs/postman-collection.json`
- **Specifications**: See `docs/openapi.yaml`

---

**Last Updated**: 2026-11-15  
**API Version**: 1.0.0  
**Swagger UI Version**: Built-in with FastAPI
