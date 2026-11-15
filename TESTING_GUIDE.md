# Phase 5 API Testing Guide

## Quick Start

### Prerequisites
- Python 3.9+
- Dependencies installed from `pyproject.toml`
- Database initialized

### Start the API Server

```bash
cd <project_root>
python -m uvicorn src.request_system.presentation.main:app --reload --host 127.0.0.1 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Run the 13 Curl Tests

Open a new terminal and run these commands:

#### Test 1: List all requests (no filters)
```bash
curl -X GET "http://localhost:8000/api/requests" \
  -H "Content-Type: application/json" | jq
```
✅ Expected: All requests with total_count, filtered_count, returned_count

#### Test 2: Filter by user_id=1
```bash
curl -X GET "http://localhost:8000/api/requests?user_id=1" \
  -H "Content-Type: application/json" | jq '.requests | length'
```
✅ Expected: Requests from user 1 only

#### Test 3: Filter by status='Новая'
```bash
curl -X GET "http://localhost:8000/api/requests?status=Новая" \
  -H "Content-Type: application/json" | jq '.filtered_count'
```
✅ Expected: Only "Новая" status requests

#### Test 4: Filter by priority='Высокий'
```bash
curl -X GET "http://localhost:8000/api/requests?priority=Высокий" \
  -H "Content-Type: application/json" | jq '.filtered_count'
```
✅ Expected: Only "Высокий" priority requests

#### Test 5: Filter by category_id=1
```bash
curl -X GET "http://localhost:8000/api/requests?category_id=1" \
  -H "Content-Type: application/json" | jq '.filtered_count'
```
✅ Expected: Only category 1 requests

#### Test 6: Full-text search 'договор'
```bash
curl -X GET "http://localhost:8000/api/requests?search=договор" \
  -H "Content-Type: application/json" | jq '.requests[0].description'
```
✅ Expected: Requests containing "договор" in description or account

#### Test 7: Search description 'оборудование'
```bash
curl -X GET "http://localhost:8000/api/requests?search_description=оборудование" \
  -H "Content-Type: application/json" | jq '.filtered_count'
```
✅ Expected: Requests with "оборудование" in description

#### Test 8: Sort by priority DESC
```bash
curl -X GET "http://localhost:8000/api/requests?sort_by=priority&sort_order=desc&limit=100" \
  -H "Content-Type: application/json" | jq '.requests[0:3] | map(.priority)'
```
✅ Expected: Priorities in descending order

#### Test 9: Sort by id ASC
```bash
curl -X GET "http://localhost:8000/api/requests?sort_by=id&sort_order=asc&limit=100" \
  -H "Content-Type: application/json" | jq '.requests[0:3] | map(.request_id)'
```
✅ Expected: IDs in ascending order

#### Test 10: Pagination - limit=5 offset=0
```bash
curl -X GET "http://localhost:8000/api/requests?limit=5&offset=0" \
  -H "Content-Type: application/json" | jq '.returned_count, .has_next, .has_previous'
```
✅ Expected: 5 results, has_next=true (if total>5), has_previous=false

#### Test 11: Pagination - limit=10 page=2
```bash
curl -X GET "http://localhost:8000/api/requests?limit=10&page=2" \
  -H "Content-Type: application/json" | jq '.offset, .has_previous'
```
✅ Expected: offset=10, has_previous=true

#### Test 12: Complex query (filters + search + sort + pagination)
```bash
curl -X GET "http://localhost:8000/api/requests?user_id=1&status=В%20работе&search=договор&sort_by=created_at&sort_order=desc&limit=10&offset=0" \
  -H "Content-Type: application/json" | jq '.requests | length, .filtered_count'
```
✅ Expected: Filtered, sorted, and paginated results

#### Test 13: Filter by account_name 'john' (substring)
```bash
curl -X GET "http://localhost:8000/api/requests?account_name=john" \
  -H "Content-Type: application/json" | jq '.requests[0].user_name'
```
✅ Expected: Requests from accounts containing "john"

---

## Run Python Tests

```bash
pytest tests/test_search_and_filtering.py -v
```

Expected output:
```
test_search_and_filtering.py::TestSearchAndFiltering::test_filter_by_user_id PASSED
test_search_and_filtering.py::TestSearchAndFiltering::test_filter_by_category_id PASSED
test_search_and_filtering.py::TestSearchAndFiltering::test_filter_by_status PASSED
... (18 tests total)

======================== 18 passed in X.XXs ========================
```

---

## Check API Documentation

Once the server is running, visit:
```
http://localhost:8000/docs
```

This opens the interactive Swagger UI with:
- All endpoints documented
- Try-it-out feature for testing
- Request/response examples
- Parameter documentation

---

## Verify Response Structure

Each successful response (200 OK) should contain:

```json
{
  "requests": [
    {
      "request_id": 1,
      "request_number": "REQ-001",
      "description": "...",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT",
      "priority": "Высокий",
      "status": "Новая",
      "registered_at": "2026-11-15T12:00:00Z"
    }
  ],
  "total_count": 100,
  "filtered_count": 15,
  "returned_count": 10,
  "limit": 10,
  "offset": 0,
  "has_next": true,
  "has_previous": false
}
```

---

## Troubleshooting

### Error: Module not found
**Solution:** Ensure PYTHONPATH is set:
```bash
export PYTHONPATH=src
python -m uvicorn src.request_system.presentation.main:app --reload
```

### Error: Port 8000 already in use
**Solution:** Use a different port:
```bash
python -m uvicorn src.request_system.presentation.main:app --port 8001
```

### Error: No database file
**Solution:** Database is initialized automatically. Delete test_db.sqlite if needed:
```bash
rm requests.db
```

### jq not installed
**Solution:** Install jq or use Python's json module:
```bash
curl ... | python -m json.tool
```

---

## Success Criteria

✅ All 13 curl tests return HTTP 200  
✅ Response contains all 8 required fields  
✅ Filters reduce result count appropriately  
✅ Sorting order is correct  
✅ Pagination works (limit respected, has_next/has_previous accurate)  
✅ All 18 Python tests pass  

**Phase 5 is COMPLETE and VERIFIED!** 🎉
