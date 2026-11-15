# Database Schema Documentation

**Version:** 1.1.0  
**Database:** SQLite 3.x  
**Last Updated:** November 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Tables](#tables)
3. [Indexes](#indexes)
4. [Relationships](#relationships)
5. [Entity Relationship Diagram](#entity-relationship-diagram)
6. [Seed Data](#seed-data)
7. [Constraints](#constraints)
8. [Best Practices](#best-practices)

---

## Overview

The Request System database schema is designed to manage a complete workflow for user requests with:
- Multi-user support with role-based access control
- Request lifecycle tracking with history
- Categorization and prioritization
- Comments and audit trails
- Attachments and result submissions
- Acceptance/rejection workflows

### Key Features

- **Foreign Key Constraints:** All relationships properly enforced
- **Indexes for Performance:** Optimized queries for searches and filters
- **Audit Trail:** RequestHistory tracks all status changes
- **Referential Integrity:** CASCADE and RESTRICT policies prevent orphaned records

---

## Tables

### Users

Stores user accounts and contact information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| `account` | TEXT | NOT NULL, UNIQUE | Username/account name (e.g., "john.doe") |
| `name` | TEXT | NOT NULL | Full name of the user |
| `contacts` | TEXT | NULLABLE | Contact information (email, phone, etc.) |

**Indexes:**
- PRIMARY KEY on `user_id`
- UNIQUE on `account`

**Sample Data:**
```sql
INSERT INTO Users (account, name, contacts) VALUES
  ('john.doe', 'John Doe', 'john.doe@company.com, ext. 1001'),
  ('jane.smith', 'Jane Smith', 'jane.smith@company.com, ext. 1002');
```

---

### Roles

Defines available user roles for authorization.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `role_id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique role identifier |
| `name` | TEXT | NOT NULL, UNIQUE | Role name (e.g., "Admin", "Executor") |

**Default Roles:**
- Admin: Full system access
- Manager: Request approval and assignment
- Executor: Task execution and completion
- User: Request submission

**Sample Data:**
```sql
INSERT INTO Roles (name) VALUES
  ('Admin'), ('Manager'), ('Executor'), ('User');
```

---

### Statuses

Represents possible request states in the workflow.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `status_id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique status identifier |
| `name` | TEXT | NOT NULL, UNIQUE | Status name (e.g., "Submitted", "In Progress") |

**Default Statuses:**
- Draft: Initial creation state
- Submitted: Ready for review
- In Progress: Currently being worked on
- Pending Review: Awaiting approval
- Approved: Ready for execution
- Rejected: Returned for revision
- Completed: Finished and delivered

**Sample Data:**
```sql
INSERT INTO Statuses (name) VALUES
  ('Draft'), ('Submitted'), ('In Progress'), ('Pending Review'),
  ('Approved'), ('Rejected'), ('Completed');
```

---

### Categories

Groups requests by type or department.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `category_id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique category identifier |
| `name` | TEXT | NOT NULL, UNIQUE | Category name |

**Default Categories:**
- IT Support
- HR & Personnel
- Finance & Accounting
- General Inquiry
- Technical Issue
- Feature Request
- Bug Report
- Infrastructure

**Sample Data:**
```sql
INSERT INTO Categories (name) VALUES
  ('IT Support'), ('HR & Personnel'), ('Finance & Accounting'),
  ('General Inquiry'), ('Technical Issue'), ('Feature Request'),
  ('Bug Report'), ('Infrastructure');
```

---

### Requests

Core table storing all user requests.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `request_id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique request identifier |
| `request_number` | TEXT | NOT NULL, UNIQUE | Human-readable request number (e.g., "REQ-2024-001") |
| `description` | TEXT | NOT NULL | Detailed request description |
| `applicant_user_id` | INTEGER | NOT NULL, FK → Users | User who submitted the request |
| `category_id` | INTEGER | NULLABLE, FK → Categories | Request category |
| `priority` | TEXT | NULLABLE | Priority level: High, Medium, Low |
| `registered_at` | TEXT | NOT NULL | ISO 8601 timestamp when request was created |

**Indexes:**
- PRIMARY KEY on `request_id`
- UNIQUE on `request_number`
- FOREIGN KEY on `applicant_user_id`
- FOREIGN KEY on `category_id`
- Index on `applicant_user_id` for filtering by user
- Index on `category_id` for filtering by category
- Index on `registered_at` for sorting by date

**Sample Data:**
```sql
INSERT INTO Requests 
  (request_number, description, applicant_user_id, category_id, priority, registered_at)
VALUES
  ('REQ-2024-001', 'Fix database connectivity issue', 1, 1, 'High', '2024-10-15T10:30:00');
```

---

### UserRoles

Join table for many-to-many relationship between Users and Roles.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | INTEGER | NOT NULL, PK, FK → Users | User identifier |
| `role_id` | INTEGER | NOT NULL, PK, FK → Roles | Role identifier |

**Composite Primary Key:** (user_id, role_id)

**Cascade Behavior:** 
- DELETE CASCADE: Deleting a user removes all role assignments

**Sample Data:**
```sql
INSERT INTO UserRoles (user_id, role_id) VALUES
  (1, 1),  -- john.doe is Admin
  (2, 2);  -- jane.smith is Manager
```

---

### Comments

User comments and service notes on requests.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `comment_id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique comment identifier |
| `request_id` | INTEGER | NOT NULL, FK → Requests | Associated request |
| `author_user_id` | INTEGER | NOT NULL, FK → Users | User who wrote the comment |
| `text` | TEXT | NOT NULL | Comment content |
| `is_service` | INTEGER | NOT NULL, 0/1 | Flag: 0=user comment, 1=internal note |
| `created_at` | TEXT | NOT NULL | ISO 8601 timestamp of comment creation |

**Indexes:**
- PRIMARY KEY on `comment_id`
- FOREIGN KEY on `request_id`
- FOREIGN KEY on `author_user_id`
- Index on `request_id` for filtering by request
- Index on `created_at` for sorting

**Sample Data:**
```sql
INSERT INTO Comments 
  (request_id, author_user_id, text, is_service, created_at)
VALUES
  (1, 2, 'Database team is investigating', 0, '2024-10-16T14:22:00');
```

---

### RequestHistory

Audit trail tracking all status transitions and changes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `history_id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique history entry identifier |
| `request_id` | INTEGER | NOT NULL, FK → Requests | Request being modified |
| `actor_user_id` | INTEGER | NOT NULL, FK → Users | User who made the change |
| `previous_status_id` | INTEGER | NULLABLE, FK → Statuses | Status before change (NULL for initial) |
| `new_status_id` | INTEGER | NOT NULL, FK → Statuses | Status after change |
| `occurred_at` | TEXT | NOT NULL | ISO 8601 timestamp of the change |
| `explanation` | TEXT | NULLABLE | Reason for the status change |

**Unique Constraint:**
- Only ONE row per request where `previous_status_id IS NULL` (initial status)

**Indexes:**
- PRIMARY KEY on `history_id`
- UNIQUE INDEX on `(request_id)` WHERE `previous_status_id IS NULL`
- Index on `(request_id, occurred_at DESC, history_id DESC)` for getting latest status

**Audit Trail Example:**
```
REQ-2024-001:
  1. NULL → Submitted (2024-10-15)
  2. Submitted → In Progress (2024-10-16)
  3. In Progress → Pending Review (2024-10-17)
  4. Pending Review → Approved (2024-10-18)
```

**Sample Data:**
```sql
INSERT INTO RequestHistory 
  (request_id, actor_user_id, previous_status_id, new_status_id, occurred_at, explanation)
VALUES
  (1, 1, NULL, 2, '2024-10-15T10:30:00', 'Initial submission'),
  (1, 2, 2, 3, '2024-10-16T09:00:00', 'Assigned to team');
```

---

### Assignments

Tracks which user is assigned to complete a request.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `assignment_id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique assignment identifier |
| `request_id` | INTEGER | NOT NULL, FK → Requests | Request being assigned |
| `assignee_user_id` | INTEGER | NOT NULL, FK → Users | User responsible for task |
| `assigned_by_user_id` | INTEGER | NOT NULL, FK → Users | User who made the assignment |
| `assigned_at` | TEXT | NOT NULL | ISO 8601 timestamp of assignment |
| `ended_at` | TEXT | NULLABLE | ISO 8601 timestamp when assignment ended |
| `reassignment_reason` | TEXT | NULLABLE | Reason for reassignment (if applicable) |

**Unique Constraint:**
- Only ONE active assignment per request (where `ended_at IS NULL`)

**Indexes:**
- PRIMARY KEY on `assignment_id`
- UNIQUE INDEX on `(request_id)` WHERE `ended_at IS NULL`
- Index on `request_id` for filtering
- Index on `assignee_user_id` for user workload

**Sample Data:**
```sql
INSERT INTO Assignments 
  (request_id, assignee_user_id, assigned_by_user_id, assigned_at, ended_at)
VALUES
  (1, 3, 2, '2024-10-16T09:00:00', NULL);
```

---

### Attachments

Files and references attached to requests.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `attachment_id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique attachment identifier |
| `request_id` | INTEGER | NOT NULL, FK → Requests | Associated request |
| `uploaded_by_user_id` | INTEGER | NOT NULL, FK → Users | User who uploaded the file |
| `reference` | TEXT | NOT NULL | File path, URL, or reference identifier |

**Indexes:**
- PRIMARY KEY on `attachment_id`
- FOREIGN KEY on `request_id`
- FOREIGN KEY on `uploaded_by_user_id`
- Index on `request_id` for filtering

**Sample Data:**
```sql
INSERT INTO Attachments (request_id, uploaded_by_user_id, reference)
VALUES (1, 2, '/uploads/req-2024-001/error-log.txt');
```

---

### ResultSubmissions

Submissions of completed work for a request.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `result_submission_id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique submission identifier |
| `request_id` | INTEGER | NOT NULL, FK → Requests | Request with submitted result |
| `executor_user_id` | INTEGER | NOT NULL, FK → Users | User submitting the work |
| `description` | TEXT | NOT NULL | Description of the submitted work |
| `submitted_at` | TEXT | NOT NULL | ISO 8601 timestamp of submission |

**Indexes:**
- PRIMARY KEY on `result_submission_id`
- FOREIGN KEY on `request_id`
- FOREIGN KEY on `executor_user_id`

**Sample Data:**
```sql
INSERT INTO ResultSubmissions 
  (request_id, executor_user_id, description, submitted_at)
VALUES
  (1, 3, 'Database connection pool fixed and tested', '2024-10-18T15:30:00');
```

---

### AcceptanceDecisions

Final approval/rejection decisions on submitted results.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `decision_id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique decision identifier |
| `result_submission_id` | INTEGER | NOT NULL, FK → ResultSubmissions | Result being reviewed |
| `controller_user_id` | INTEGER | NOT NULL, FK → Users | User making the decision |
| `outcome` | TEXT | NOT NULL | Decision: 'accepted' or 'rework' |
| `comment` | TEXT | NULLABLE | Decision comment or rejection reason |
| `decided_at` | TEXT | NOT NULL | ISO 8601 timestamp of decision |

**Constraint:**
- If outcome='rework', comment MUST be provided (non-null and non-empty)

**Indexes:**
- PRIMARY KEY on `decision_id`
- FOREIGN KEY on `result_submission_id`
- FOREIGN KEY on `controller_user_id`

**Sample Data:**
```sql
INSERT INTO AcceptanceDecisions 
  (result_submission_id, controller_user_id, outcome, comment, decided_at)
VALUES
  (1, 2, 'accepted', 'Solution verified and working correctly', '2024-10-19T10:00:00');
```

---

## Indexes

### Performance Indexes

| Index | Table | Columns | Type | Purpose |
|-------|-------|---------|------|---------|
| `idx_request_history_one_initial_status` | RequestHistory | request_id | UNIQUE WHERE | Ensure single initial status |
| `idx_request_history_latest` | RequestHistory | request_id, occurred_at DESC, history_id DESC | BTREE | Get latest status efficiently |
| `idx_assignments_one_active_per_request` | Assignments | request_id | UNIQUE WHERE | Ensure single active assignment |

### Recommended Additional Indexes (for optimization)

```sql
-- User queries
CREATE INDEX idx_users_account ON Users(account);

-- Request filtering
CREATE INDEX idx_requests_applicant_user_id ON Requests(applicant_user_id);
CREATE INDEX idx_requests_category_id ON Requests(category_id);
CREATE INDEX idx_requests_registered_at ON Requests(registered_at DESC);
CREATE INDEX idx_requests_priority ON Requests(priority);

-- Comment queries
CREATE INDEX idx_comments_request_id ON Comments(request_id);
CREATE INDEX idx_comments_author_user_id ON Comments(author_user_id);
CREATE INDEX idx_comments_created_at ON Comments(created_at DESC);

-- Assignment tracking
CREATE INDEX idx_assignments_assignee_user_id ON Assignments(assignee_user_id);
CREATE INDEX idx_assignments_assigned_by ON Assignments(assigned_by_user_id);

-- Attachment queries
CREATE INDEX idx_attachments_request_id ON Attachments(request_id);
CREATE INDEX idx_attachments_uploaded_by ON Attachments(uploaded_by_user_id);

-- Result submission tracking
CREATE INDEX idx_result_submissions_request_id ON ResultSubmissions(request_id);
CREATE INDEX idx_result_submissions_executor ON ResultSubmissions(executor_user_id);

-- Decision tracking
CREATE INDEX idx_acceptance_decisions_submission ON AcceptanceDecisions(result_submission_id);
CREATE INDEX idx_acceptance_decisions_controller ON AcceptanceDecisions(controller_user_id);
```

---

## Relationships

### Foreign Key Constraints

All foreign keys use explicit constraint names for clarity.

| Constraint | From | To | Behavior |
|-----------|------|----|---------| 
| `FK Users` | Requests.applicant_user_id | Users.user_id | RESTRICT (cannot delete users with requests) |
| `FK Categories` | Requests.category_id | Categories.category_id | RESTRICT |
| `FK Users in UserRoles` | UserRoles.user_id | Users.user_id | CASCADE (delete roles when user deleted) |
| `FK Roles in UserRoles` | UserRoles.role_id | Roles.role_id | CASCADE |
| `FK Requests in Comments` | Comments.request_id | Requests.request_id | RESTRICT |
| `FK Users in Comments` | Comments.author_user_id | Users.user_id | RESTRICT |
| `FK Requests in History` | RequestHistory.request_id | Requests.request_id | RESTRICT |
| `FK Users in History` | RequestHistory.actor_user_id | Users.user_id | RESTRICT |
| `FK Statuses (prev)` | RequestHistory.previous_status_id | Statuses.status_id | RESTRICT |
| `FK Statuses (new)` | RequestHistory.new_status_id | Statuses.status_id | RESTRICT |

### Relationship Types

1. **One-to-Many (1:N)**
   - Users → Requests (one user submits many requests)
   - Users → Comments (one user writes many comments)
   - Users → RequestHistory (one user makes many changes)
   - Requests → Comments (one request has many comments)
   - Requests → RequestHistory (one request has many status changes)
   - Requests → Assignments (one request has many assignments over time)
   - Categories → Requests (one category has many requests)

2. **Many-to-Many (M:N)**
   - Users ↔ Roles (via UserRoles join table)

---

## Entity Relationship Diagram

```
┌─────────────┐
│    Users    │
├─────────────┤
│ user_id (PK)│
│ account     │
│ name        │
│ contacts    │
└──────┬──────┘
       │
       ├──────────────┬─────────────────┬──────────────┐
       │              │                 │              │
       │       ┌──────▼────────┐  ┌─────▼──────┐  ┌───▼──────────┐
       │       │  UserRoles    │  │ Requests   │  │  Comments    │
       │       ├───────────────┤  ├────────────┤  ├──────────────┤
       │       │user_id (PK,FK)│  │request_id  │  │comment_id    │
       │       │role_id (PK,FK)│  │request_num │  │request_id(FK)│
       │       └────────────────┘  │applicant.. │  │author_id(FK) │
       │              ▲             │category.. │  │text          │
       │              │             │priority   │  │is_service    │
       │       ┌──────┴──────┐      │registered │  │created_at    │
       │       │    Roles    │      └──────┬────┘  └──────────────┘
       │       ├─────────────┤             │
       │       │ role_id (PK)│             ├──────────────┬──────────────┐
       │       │ name        │             │              │              │
       │       └─────────────┘      ┌──────▼───────┐  ┌──▼─────────┐  ┌─▼──────────┐
       │                            │RequestHistory│  │Assignments │  │Attachments │
       │                            ├──────────────┤  ├────────────┤  ├────────────┤
       │                            │history_id    │  │assignment..│  │attachment..│
       │                            │request_id(FK)│  │request_id..│  │request_id..│
       │                            │actor_id(FK)  │  │assignee_id │  │uploaded_by │
       │                            │prev_status   │  │assigned_by │  │reference   │
       │                            │new_status(FK)│  │assigned_at │  └────────────┘
       │                            │occurred_at   │  │ended_at    │
       │                            │explanation   │  │reason      │
       │                            └──────────────┘  └────────────┘
       │
       ├────────────────────┬─────────────────────────────────────┐
       │                    │                                     │
┌──────▼────────┐  ┌────────▼──────────┐            ┌──────────────▼────┐
│  Categories   │  │   Statuses       │            │ResultSubmissions   │
├───────────────┤  ├──────────────────┤            ├────────────────────┤
│category_id(PK)│  │status_id (PK)    │            │result_sub_id (PK)  │
│name           │  │name              │            │request_id (FK)     │
└───────────────┘  └──────────────────┘            │executor_id (FK)    │
                                                    │description        │
                                                    │submitted_at       │
                                                    └────────────┬───────┘
                                                                 │
                                                    ┌────────────▼─────────────┐
                                                    │AcceptanceDecisions      │
                                                    ├─────────────────────────┤
                                                    │decision_id (PK)         │
                                                    │result_submission_id(FK) │
                                                    │controller_id (FK)       │
                                                    │outcome (accepted/rework)│
                                                    │comment                  │
                                                    │decided_at              │
                                                    └─────────────────────────┘
```

---

## Seed Data

The database comes pre-populated with:

### Default Records

| Entity | Count | Details |
|--------|-------|---------|
| Roles | 4 | Admin, Manager, Executor, User |
| Statuses | 7 | Draft, Submitted, In Progress, Pending Review, Approved, Rejected, Completed |
| Categories | 8 | IT Support, HR, Finance, Inquiry, Technical, Feature, Bug, Infrastructure |
| Users | 10 | Test users with diverse roles |

### Sample Data

| Entity | Count | Details |
|--------|-------|---------|
| Requests | 20 | Various statuses and priorities from past 30 days |
| RequestHistory | 20+ | Status transitions for each request |
| Comments | 13 | Sample user and service comments |
| UserRoles | 10 | Role assignments for test users |

Load seed data with:
```bash
# Initialize and load seed data
python -m request_system.scripts.load_seed_data --reset-db

# Or use the convenience script
bash scripts/init-db.sh --reset
```

---

## Constraints

### Column Constraints

```sql
-- Users table
CHECK (length(trim(account)) > 0)
CHECK (length(trim(name)) > 0)

-- Roles table
CHECK (length(trim(name)) > 0)

-- Statuses table
CHECK (length(trim(name)) > 0)

-- Categories table
CHECK (length(trim(name)) > 0)

-- Requests table
CHECK (length(trim(request_number)) > 0)
CHECK (length(trim(description)) > 0)

-- Comments table
CHECK (length(trim(text)) > 0)
CHECK (is_service IN (0, 1))

-- AcceptanceDecisions table
CHECK (outcome IN ('accepted', 'rework'))
CHECK (outcome <> 'rework' OR (comment IS NOT NULL AND length(trim(comment)) > 0))
```

### Uniqueness Constraints

| Table | Column(s) | Enforcement |
|-------|-----------|-------------|
| Users | account | Database UNIQUE constraint |
| Roles | name | Database UNIQUE constraint |
| Statuses | name | Database UNIQUE constraint |
| Categories | name | Database UNIQUE constraint |
| Requests | request_number | Database UNIQUE constraint |
| UserRoles | (user_id, role_id) | Composite PRIMARY KEY |
| RequestHistory | request_id WHERE previous_status_id IS NULL | Unique index |
| Assignments | request_id WHERE ended_at IS NULL | Unique index |

---

## Best Practices

### Query Patterns

**Get current request status:**
```sql
SELECT new_status_id, occurred_at
FROM RequestHistory
WHERE request_id = ?
ORDER BY occurred_at DESC, history_id DESC
LIMIT 1;
```

**Get request history (timeline):**
```sql
SELECT h.*, s1.name as previous_status, s2.name as new_status, u.name as actor
FROM RequestHistory h
LEFT JOIN Statuses s1 ON h.previous_status_id = s1.status_id
LEFT JOIN Statuses s2 ON h.new_status_id = s2.status_id
LEFT JOIN Users u ON h.actor_user_id = u.user_id
WHERE h.request_id = ?
ORDER BY h.occurred_at, h.history_id;
```

**Get user's active assignment:**
```sql
SELECT * FROM Assignments
WHERE assignee_user_id = ? AND ended_at IS NULL
LIMIT 1;
```

**Filter requests with pagination:**
```sql
SELECT r.*, c.name as category, s.name as status
FROM Requests r
LEFT JOIN Categories c ON r.category_id = c.category_id
WHERE r.applicant_user_id = ?
  AND r.priority = ?
ORDER BY r.registered_at DESC
LIMIT ? OFFSET ?;
```

### Maintenance

- **Backup:** Regular SQLite database file backups (e.g., daily)
- **Vacuum:** Run `VACUUM` periodically to reclaim space
- **Integrity Check:** `PRAGMA integrity_check;` for verification
- **Foreign Key Validation:** `PRAGMA foreign_key_check;` for constraints

### Performance Tips

1. **Indexes:** Use provided indexes for common queries
2. **Batch Operations:** Group INSERT/UPDATE statements in transactions
3. **Pagination:** Always use LIMIT/OFFSET for large result sets
4. **Selective Columns:** Avoid SELECT * for large tables
5. **JOIN Optimization:** Index foreign key columns

---

**Document Version:** 1.1.0  
**Last Updated:** November 15, 2026
