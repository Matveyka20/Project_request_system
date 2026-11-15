# API Testing Guide for QA Team

Complete step-by-step guide for testing the Request Management System API with all search, filtering, sorting, and pagination capabilities.

---

## 📋 Quick Start

### Prerequisites
- Python 3.9+
- FastAPI installed
- curl or Postman/Insomnia
- Terminal/Command Prompt access

### 1. Start the API Server

Navigate to project root and start uvicorn:

```bash
# On Linux/Mac:
python -m uvicorn src.request_system.presentation.main:app --reload --host 0.0.0.0 --port 8000

# On Windows (PowerShell):
python -m uvicorn src.request_system.presentation.main:app --reload --host 0.0.0.0 --port 8000

# On Windows (Command Prompt):
python -m uvicorn src.request_system.presentation.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 2. Verify Server is Running

```bash
curl -X GET "http://localhost:8000/health"
```

**Expected Response:**
```json
{"status": "ok"}
```

---

## 🧪 Test Scenarios

### Test 1: Basic List (No Filters)

**Objective:** Verify API returns all requests with default pagination

**Command:**
```bash
curl -X GET "http://localhost:8000/api/requests" \
  -H "Content-Type: application/json"
```

**Expected Results:**
- ✅ HTTP Status: 200
- ✅ Response contains `requests` array
- ✅ Response contains metadata: `total_count`, `filtered_count`, `returned_count`
- ✅ Response contains pagination: `limit`, `offset`, `has_next`, `has_previous`
- ✅ Default limit is 10
- ✅ Default offset is 0
- ✅ Each request contains: request_id, request_number, description, status, priority, etc.

**Validation Checklist:**
- [ ] HTTP 200 OK
- [ ] Response is valid JSON
- [ ] `requests` array has elements (should be ≤ 10)
- [ ] `total_count` ≥ `filtered_count` ≥ `returned_count`
- [ ] `returned_count` ≤ `limit`
- [ ] All request objects have required fields

---

### Test 2: Filter by User ID

**Objective:** Verify filtering by user_id narrows results to that user's requests

**Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?user_id=1" \
  -H "Content-Type: application/json"
```

**Expected Results:**
- ✅ HTTP Status: 200
- ✅ `filtered_count` ≤ `total_count`
- ✅ All returned requests have `applicant_user_id` = 1
- ✅ Response metadata correctly reflects filtered count

**Validation Checklist:**
- [ ] HTTP 200 OK
- [ ] `filtered_count` shows reduced number of results
- [ ] Every request in array has `applicant_user_id: 1`
- [ ] `returned_count` matches actual number of items returned
- [ ] `has_previous` is false (since offset=0)

**Additional Tests:**
- Test with user_id=2: should return different results
- Test with user_id=999: should return empty array

---

### Test 3: Filter by Status

**Objective:** Verify filtering by status works correctly

**Commands to Test:**

```bash
# Test with status=New
curl -X GET "http://localhost:8000/api/requests?status=New" \
  -H "Content-Type: application/json"

# Test with status=In Progress
curl -X GET "http://localhost:8000/api/requests?status=In%20Progress" \
  -H "Content-Type: application/json"

# Test with status=Completed
curl -X GET "http://localhost:8000/api/requests?status=Completed" \
  -H "Content-Type: application/json"
```

**Expected Results:**
- ✅ All returned requests have matching status
- ✅ Different status values return different results
- ✅ Case-sensitive matching (status values are fixed strings)

**Validation Checklist:**
- [ ] All items in response have matching status value
- [ ] Different status filters produce different results
- [ ] Response count is consistent

**Valid Status Values:**
- New
- In Progress
- Under Review
- Approved
- Rejected
- Completed

---

### Test 4: Filter by Priority

**Objective:** Verify filtering by priority level works

**Commands to Test:**

```bash
# Test with priority=High
curl -X GET "http://localhost:8000/api/requests?priority=High" \
  -H "Content-Type: application/json"

# Test with priority=Critical
curl -X GET "http://localhost:8000/api/requests?priority=Critical" \
  -H "Content-Type: application/json"

# Test with priority=Low
curl -X GET "http://localhost:8000/api/requests?priority=Low" \
  -H "Content-Type: application/json"
```

**Expected Results:**
- ✅ All returned requests have matching priority
- ✅ Different priority values return different results

**Validation Checklist:**
- [ ] All items have matching priority value
- [ ] Different priorities produce different result counts

**Valid Priority Values:**
- Low
- Medium
- High
- Critical

---

### Test 5: Filter by Category ID

**Objective:** Verify category filtering works

**Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?category_id=1" \
  -H "Content-Type: application/json"
```

**Expected Results:**
- ✅ All returned requests have `category_id` = 1
- ✅ Filtered count is accurate

**Validation Checklist:**
- [ ] All items have `category_id: 1`
- [ ] Metadata counts are accurate

---

### Test 6: Full-Text Search

**Objective:** Verify full-text search works across description and account_name

**Commands to Test:**

```bash
# Search for "laptop"
curl -X GET "http://localhost:8000/api/requests?search=laptop" \
  -H "Content-Type: application/json"

# Search for "equipment"
curl -X GET "http://localhost:8000/api/requests?search=equipment" \
  -H "Content-Type: application/json"

# Search for "software"
curl -X GET "http://localhost:8000/api/requests?search=software" \
  -H "Content-Type: application/json"
```

**Expected Results:**
- ✅ Results contain search term in either description or user_name
- ✅ Search is case-insensitive
- ✅ Search is substring matching (partial matches work)

**Validation Checklist:**
- [ ] All returned items contain search term somewhere
- [ ] Lowercase and uppercase variations work
- [ ] Partial matches are found (e.g., searching "equip" finds "equipment")

---

### Test 7: Search in Description Only

**Objective:** Verify search_description parameter searches only in description field

**Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?search_description=equipment" \
  -H "Content-Type: application/json"
```

**Expected Results:**
- ✅ All returned items have "equipment" in description field
- ✅ Items with term in user_name but not description are excluded

**Validation Checklist:**
- [ ] Only description field is searched
- [ ] Results don't include matches in other fields

---

### Test 8: Sort by Priority (Descending)

**Objective:** Verify sorting by priority in descending order (Critical → Low)

**Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?sort_by=priority&sort_order=desc" \
  -H "Content-Type: application/json"
```

**Expected Results:**
- ✅ Results are sorted: Critical → High → Medium → Low
- ✅ First item has highest priority

**Priority Order (desc):**
1. Critical (highest)
2. High
3. Medium
4. Low (lowest)

**Validation Checklist:**
- [ ] First item is Critical (if exists)
- [ ] Last item is Low (if exists)
- [ ] Priority order is correct throughout

---

### Test 9: Sort by ID (Ascending)

**Objective:** Verify sorting by ID in ascending order (1, 2, 3, ...)

**Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?sort_by=id&sort_order=asc" \
  -H "Content-Type: application/json"
```

**Expected Results:**
- ✅ Results are sorted by ID from lowest to highest
- ✅ Each subsequent request_id is >= previous one

**Validation Checklist:**
- [ ] IDs increase from left to right
- [ ] No out-of-order items

---

### Test 10: Pagination with Limit and Offset

**Objective:** Verify limit+offset pagination works correctly

**Commands to Test:**

```bash
# Get first 2 items
curl -X GET "http://localhost:8000/api/requests?limit=2&offset=0" \
  -H "Content-Type: application/json"

# Get next 2 items (offset=2)
curl -X GET "http://localhost:8000/api/requests?limit=2&offset=2" \
  -H "Content-Type: application/json"

# Get next 2 items (offset=4)
curl -X GET "http://localhost:8000/api/requests?limit=2&offset=4" \
  -H "Content-Type: application/json"
```

**Expected Results:**
- ✅ First request returns offset=0, returned_count=2, has_next=true
- ✅ Second request returns offset=2, returned_count=2, has_next=true, has_previous=true
- ✅ Third request returns offset=4, no duplicate items from previous requests
- ✅ Items change between requests (pagination is working)

**Validation Checklist:**
- [ ] Limit is respected (max 2 items returned)
- [ ] Offset changes correctly
- [ ] No duplicate items across pages
- [ ] has_next/has_previous accurate
- [ ] Items appear in consistent order

---

### Test 11: Pagination with Page Parameter

**Objective:** Verify page-based pagination (alternative to offset)

**Commands to Test:**

```bash
# Get page 1
curl -X GET "http://localhost:8000/api/requests?limit=2&page=1" \
  -H "Content-Type: application/json"

# Get page 2
curl -X GET "http://localhost:8000/api/requests?limit=2&page=2" \
  -H "Content-Type: application/json"

# Get page 3
curl -X GET "http://localhost:8000/api/requests?limit=2&page=3" \
  -H "Content-Type: application/json"
```

**Expected Behavior:**
- page=1 should equal offset=0
- page=2 should equal offset=2
- page=3 should equal offset=4

**Validation Checklist:**
- [ ] Page=1 returns offset=0
- [ ] Page=2 returns offset=2
- [ ] Page=3 returns offset=4
- [ ] Items are same as offset-based pagination
- [ ] has_previous=false for page=1

---

### Test 12: Combined Query (Filters + Search + Sort + Pagination)

**Objective:** Verify all parameters work together correctly

**Command:**
```bash
curl -X GET "http://localhost:8000/api/requests?user_id=1&status=In%20Progress&search=equipment&sort_by=created_at&sort_order=desc&limit=10&offset=0" \
  -H "Content-Type: application/json"
```

**Expected Results:**
- ✅ Results match ALL criteria:
  - applicant_user_id = 1
  - status = "In Progress"
  - description or user_name contains "equipment"
  - sorted by created_at descending
  - paginated with limit=10, offset=0

**Validation Checklist:**
- [ ] All filters are applied (AND logic)
- [ ] Results are sorted by created_at descending
- [ ] Pagination is working
- [ ] filtered_count reflects all filters
- [ ] Number of results is reasonable

---

### Test 13: Filter by Account Name

**Objective:** Verify substring matching on account_name (user_name)

**Commands to Test:**

```bash
# Search for "John"
curl -X GET "http://localhost:8000/api/requests?account_name=John" \
  -H "Content-Type: application/json"

# Search for "jane"
curl -X GET "http://localhost:8000/api/requests?account_name=jane" \
  -H "Content-Type: application/json"

# Search for "oe" (partial match)
curl -X GET "http://localhost:8000/api/requests?account_name=oe" \
  -H "Content-Type: application/json"
```

**Expected Results:**
- ✅ Case-insensitive matching (John, john, JOHN all work)
- ✅ Substring matching (partial names work)
- ✅ user_name contains the search term

**Validation Checklist:**
- [ ] Case-insensitive matching works
- [ ] Partial matches are found
- [ ] All returned items have user_name containing the term

---

## 🚨 Error Case Testing

### Invalid Limit (> 100)

```bash
curl -X GET "http://localhost:8000/api/requests?limit=200"
```

**Expected:**
- ✅ HTTP 422 Unprocessable Entity
- ✅ Error message about limit exceeding maximum (100)

---

### Invalid Status

```bash
curl -X GET "http://localhost:8000/api/requests?status=InvalidStatus"
```

**Expected:**
- ✅ HTTP 422 Unprocessable Entity
- ✅ Error lists valid status values

---

### Invalid Priority

```bash
curl -X GET "http://localhost:8000/api/requests?priority=VeryHigh"
```

**Expected:**
- ✅ HTTP 422 Unprocessable Entity
- ✅ Error lists valid priority values

---

### Negative User ID

```bash
curl -X GET "http://localhost:8000/api/requests?user_id=-1"
```

**Expected:**
- ✅ HTTP 422 Unprocessable Entity
- ✅ Error indicates user_id must be ≥ 1

---

### Negative Offset

```bash
curl -X GET "http://localhost:8000/api/requests?offset=-5"
```

**Expected:**
- ✅ HTTP 422 Unprocessable Entity
- ✅ Error indicates offset must be ≥ 0

---

## ✅ Overall Success Criteria

A complete test pass should verify:

| Aspect | Tests | Status |
|--------|-------|--------|
| **Basic Operations** | Test 1 (basic list) | ✅ |
| **Single Filters** | Tests 2-5 (user, status, priority, category) | ✅ |
| **Search Functions** | Tests 6-7 (full-text, description) | ✅ |
| **Sorting** | Tests 8-9 (priority, ID) | ✅ |
| **Pagination** | Tests 10-11 (offset, page) | ✅ |
| **Combined Queries** | Test 12 (complex query) | ✅ |
| **Account Name Filter** | Test 13 (substring matching) | ✅ |
| **Error Handling** | 5+ error cases | ✅ |
| **Response Structure** | All responses match schema | ✅ |
| **HTTP Status Codes** | 200 for valid, 422 for invalid | ✅ |

---

## 📊 Postman Collection

For easier testing with Postman/Insomnia:

1. Open Postman
2. Click "Import"
3. Select `docs/postman-collection.json`
4. All 13 test scenarios are pre-configured
5. Run with "Run Collection" for automated testing

---

## 🔍 Debugging Tips

### Problem: Server won't start
**Solution:** 
- Check Python version (need 3.9+)
- Verify FastAPI is installed: `pip install fastapi uvicorn`
- Try with explicit host: `--host 127.0.0.1`

### Problem: Port 8000 already in use
**Solution:**
- Kill process on port 8000: `lsof -ti:8000 | xargs kill` (Mac/Linux)
- Use different port: `--port 8001`

### Problem: curl: command not found
**Solution:**
- Install curl or use Postman/Insomnia instead
- Or use Python: `python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/api/requests').read())"`

### Problem: 404 Not Found
**Solution:**
- Verify API is running: `curl http://localhost:8000/health`
- Check endpoint path is correct: `/api/requests`

### Problem: Response is empty
**Solution:**
- Database might be empty - check test data is loaded
- Try without filters first: `curl http://localhost:8000/api/requests`

---

## 📝 Test Report Template

Create a test report with the following format:

```markdown
# Test Execution Report

**Date:** [DATE]
**Tester:** [NAME]
**Environment:** [DEV/STAGING/PROD]
**API Version:** 1.0.0

## Summary
- Total Tests: 13+
- Passed: X
- Failed: X
- Blocked: X

## Detailed Results

### Test 1: Basic List
- Status: ✅ PASS / ❌ FAIL
- Notes: [Any observations]

### Test 2: Filter by User ID
- Status: ✅ PASS / ❌ FAIL
- Notes: [Any observations]

... (continue for all tests)

## Overall Result
✅ **API READY FOR PRODUCTION** / ❌ **NOT READY - Issues Found**

## Known Issues
- [Issue 1]
- [Issue 2]

## Recommendations
- [Recommendation 1]
- [Recommendation 2]
```

---

## 🎯 Performance Baseline

For comparison during load testing:

| Operation | Expected Time | Max Allowed |
|-----------|----------------|------------|
| Basic list | < 100ms | 500ms |
| Filter + search | < 200ms | 1000ms |
| Pagination (large offset) | < 300ms | 1500ms |
| Combined complex query | < 400ms | 2000ms |

---

## 📚 Additional Resources

- **API Documentation:** `docs/search-and-filtering.md`
- **Response Examples:** `docs/api-response-examples.md`
- **OpenAPI Spec:** `docs/openapi.yaml`
- **Postman Collection:** `docs/postman-collection.json`
- **GitHub Repository:** [Link to repo]

---

**Last Updated:** 2026-11-15
**Status:** Ready for QA Testing
