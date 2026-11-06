-- SQLite schema for a new Request System database.
-- Run from PowerShell at the repository root with:
-- Get-Content docs/sql/schema.sql | sqlite3 request-system.db
-- Each request's initial RequestHistory row must be inserted in the same
-- application transaction as the Requests row; current status is the latest
-- RequestHistory.new_status_id (ordered by occurred_at, then history_id).

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY,
    account TEXT NOT NULL UNIQUE CHECK (length(trim(account)) > 0),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    contacts TEXT
);

CREATE TABLE IF NOT EXISTS Roles (
    role_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0)
);

CREATE TABLE IF NOT EXISTS Statuses (
    status_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0)
);

CREATE TABLE IF NOT EXISTS Categories (
    category_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0)
);

CREATE TABLE IF NOT EXISTS Requests (
    request_id INTEGER PRIMARY KEY,
    request_number TEXT NOT NULL UNIQUE CHECK (length(trim(request_number)) > 0),
    description TEXT NOT NULL CHECK (length(trim(description)) > 0),
    applicant_user_id INTEGER NOT NULL,
    category_id INTEGER,
    priority TEXT,
    registered_at TEXT NOT NULL,
    FOREIGN KEY (applicant_user_id) REFERENCES Users (user_id) ON DELETE RESTRICT,
    FOREIGN KEY (category_id) REFERENCES Categories (category_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS UserRoles (
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES Roles (role_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Comments (
    comment_id INTEGER PRIMARY KEY,
    request_id INTEGER NOT NULL,
    author_user_id INTEGER NOT NULL,
    text TEXT NOT NULL CHECK (length(trim(text)) > 0),
    is_service INTEGER NOT NULL CHECK (is_service IN (0, 1)),
    created_at TEXT NOT NULL,
    FOREIGN KEY (request_id) REFERENCES Requests (request_id) ON DELETE RESTRICT,
    FOREIGN KEY (author_user_id) REFERENCES Users (user_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS RequestHistory (
    history_id INTEGER PRIMARY KEY,
    request_id INTEGER NOT NULL,
    actor_user_id INTEGER NOT NULL,
    previous_status_id INTEGER,
    new_status_id INTEGER NOT NULL,
    occurred_at TEXT NOT NULL,
    explanation TEXT,
    FOREIGN KEY (request_id) REFERENCES Requests (request_id) ON DELETE RESTRICT,
    FOREIGN KEY (actor_user_id) REFERENCES Users (user_id) ON DELETE RESTRICT,
    FOREIGN KEY (previous_status_id) REFERENCES Statuses (status_id) ON DELETE RESTRICT,
    FOREIGN KEY (new_status_id) REFERENCES Statuses (status_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Assignments (
    assignment_id INTEGER PRIMARY KEY,
    request_id INTEGER NOT NULL,
    assignee_user_id INTEGER NOT NULL,
    assigned_by_user_id INTEGER NOT NULL,
    assigned_at TEXT NOT NULL,
    ended_at TEXT,
    reassignment_reason TEXT,
    FOREIGN KEY (request_id) REFERENCES Requests (request_id) ON DELETE RESTRICT,
    FOREIGN KEY (assignee_user_id) REFERENCES Users (user_id) ON DELETE RESTRICT,
    FOREIGN KEY (assigned_by_user_id) REFERENCES Users (user_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Attachments (
    attachment_id INTEGER PRIMARY KEY,
    request_id INTEGER NOT NULL,
    uploaded_by_user_id INTEGER NOT NULL,
    reference TEXT NOT NULL CHECK (length(trim(reference)) > 0),
    FOREIGN KEY (request_id) REFERENCES Requests (request_id) ON DELETE RESTRICT,
    FOREIGN KEY (uploaded_by_user_id) REFERENCES Users (user_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS ResultSubmissions (
    result_submission_id INTEGER PRIMARY KEY,
    request_id INTEGER NOT NULL,
    executor_user_id INTEGER NOT NULL,
    description TEXT NOT NULL CHECK (length(trim(description)) > 0),
    submitted_at TEXT NOT NULL,
    FOREIGN KEY (request_id) REFERENCES Requests (request_id) ON DELETE RESTRICT,
    FOREIGN KEY (executor_user_id) REFERENCES Users (user_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS AcceptanceDecisions (
    decision_id INTEGER PRIMARY KEY,
    result_submission_id INTEGER NOT NULL,
    controller_user_id INTEGER NOT NULL,
    outcome TEXT NOT NULL CHECK (outcome IN ('accepted', 'rework')),
    comment TEXT,
    decided_at TEXT NOT NULL,
    CHECK (
        outcome <> 'rework'
        OR (comment IS NOT NULL AND length(trim(comment)) > 0)
    ),
    FOREIGN KEY (result_submission_id)
        REFERENCES ResultSubmissions (result_submission_id) ON DELETE RESTRICT,
    FOREIGN KEY (controller_user_id) REFERENCES Users (user_id) ON DELETE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_request_history_one_initial_status
    ON RequestHistory (request_id)
    WHERE previous_status_id IS NULL;

CREATE INDEX IF NOT EXISTS idx_request_history_latest
    ON RequestHistory (request_id, occurred_at DESC, history_id DESC);

CREATE UNIQUE INDEX IF NOT EXISTS idx_assignments_one_active_per_request
    ON Assignments (request_id)
    WHERE ended_at IS NULL;
