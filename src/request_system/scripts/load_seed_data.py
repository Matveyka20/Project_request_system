#!/usr/bin/env python3
"""
Database initialization script that loads seed data into the request system.

This script creates categories, statuses, test users, and sample requests
for development and testing purposes.

Usage:
    python -m request_system.scripts.load_seed_data
    python -m request_system.scripts.load_seed_data --reset-db
    python -m request_system.scripts.load_seed_data --database requests.db
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import argparse
import sqlite3

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from request_system.application.ports.persistence import PersistenceError
from request_system.infrastructure.database.sqlite import SQLiteDatabase


def load_seed_data(database: sqlite3.Connection) -> None:
    """Load seed data into the database."""
    
    # =========================================================================
    # 1. Load Default Roles
    # =========================================================================
    roles = [
        ("Admin",),
        ("Manager",),
        ("Executor",),
        ("User",),
    ]
    database.execute("DELETE FROM UserRoles")
    database.execute("DELETE FROM Roles")
    cursor = database.executemany("INSERT INTO Roles (name) VALUES (?)", roles)
    print(f"✓ Loaded {cursor.rowcount} roles")
    
    # =========================================================================
    # 2. Load Default Statuses
    # =========================================================================
    statuses = [
        ("Draft",),
        ("Submitted",),
        ("In Progress",),
        ("Pending Review",),
        ("Approved",),
        ("Rejected",),
        ("Completed",),
    ]
    database.execute("DELETE FROM Statuses")
    cursor = database.executemany("INSERT INTO Statuses (name) VALUES (?)", statuses)
    print(f"✓ Loaded {cursor.rowcount} statuses")
    
    # =========================================================================
    # 3. Load Categories
    # =========================================================================
    categories = [
        ("IT Support",),
        ("HR & Personnel",),
        ("Finance & Accounting",),
        ("General Inquiry",),
        ("Technical Issue",),
        ("Feature Request",),
        ("Bug Report",),
        ("Infrastructure",),
    ]
    database.execute("DELETE FROM Categories")
    cursor = database.executemany("INSERT INTO Categories (name) VALUES (?)", categories)
    print(f"✓ Loaded {cursor.rowcount} categories")
    
    # =========================================================================
    # 4. Load Test Users
    # =========================================================================
    test_users = [
        ("john.doe", "John Doe", "john.doe@company.com, ext. 1001"),
        ("jane.smith", "Jane Smith", "jane.smith@company.com, ext. 1002"),
        ("bob.johnson", "Bob Johnson", "bob.johnson@company.com, ext. 1003"),
        ("alice.williams", "Alice Williams", "alice.williams@company.com, ext. 1004"),
        ("charlie.brown", "Charlie Brown", "charlie.brown@company.com, ext. 1005"),
        ("diana.prince", "Diana Prince", "diana.prince@company.com, ext. 1006"),
        ("eddie.murphy", "Eddie Murphy", "eddie.murphy@company.com, ext. 1007"),
        ("fiona.green", "Fiona Green", "fiona.green@company.com, ext. 1008"),
        ("george.harris", "George Harris", "george.harris@company.com, ext. 1009"),
        ("hannah.lee", "Hannah Lee", "hannah.lee@company.com, ext. 1010"),
    ]
    database.execute("DELETE FROM Users")
    cursor = database.executemany(
        "INSERT INTO Users (account, name, contacts) VALUES (?, ?, ?)",
        test_users
    )
    print(f"✓ Loaded {cursor.rowcount} test users")
    
    # Get user IDs
    users = database.execute("SELECT user_id, account FROM Users ORDER BY user_id").fetchall()
    user_map = {account: uid for uid, account in users}
    
    # Get role IDs
    roles_result = database.execute("SELECT role_id, name FROM Roles ORDER BY role_id").fetchall()
    role_map = {name: rid for rid, name in roles_result}
    
    # =========================================================================
    # 5. Assign Roles to Users
    # =========================================================================
    user_roles = [
        (user_map["john.doe"], role_map["Admin"]),
        (user_map["jane.smith"], role_map["Manager"]),
        (user_map["bob.johnson"], role_map["Executor"]),
        (user_map["alice.williams"], role_map["Executor"]),
        (user_map["charlie.brown"], role_map["User"]),
        (user_map["diana.prince"], role_map["Manager"]),
        (user_map["eddie.murphy"], role_map["Executor"]),
        (user_map["fiona.green"], role_map["User"]),
        (user_map["george.harris"], role_map["User"]),
        (user_map["hannah.lee"], role_map["Executor"]),
    ]
    cursor = database.executemany(
        "INSERT INTO UserRoles (user_id, role_id) VALUES (?, ?)",
        user_roles
    )
    print(f"✓ Assigned {cursor.rowcount} user roles")
    
    # Get category and status IDs
    categories_result = database.execute(
        "SELECT category_id, name FROM Categories ORDER BY category_id"
    ).fetchall()
    category_map = {name: cid for cid, name in categories_result}
    
    statuses_result = database.execute(
        "SELECT status_id, name FROM Statuses ORDER BY status_id"
    ).fetchall()
    status_map = {name: sid for sid, name in statuses_result}
    
    # =========================================================================
    # 6. Load Sample Requests
    # =========================================================================
    base_date = datetime.now()
    requests_data = [
        # Format: (request_number, description, applicant_user_id, category_id, priority, registered_at)
        ("REQ-2024-001", "Fix critical database connectivity issue", user_map["bob.johnson"], category_map["IT Support"], "High", (base_date - timedelta(days=30)).isoformat()),
        ("REQ-2024-002", "Deploy new authentication module", user_map["alice.williams"], category_map["Technical Issue"], "High", (base_date - timedelta(days=28)).isoformat()),
        ("REQ-2024-003", "Update employee handbook", user_map["charlie.brown"], category_map["HR & Personnel"], "Medium", (base_date - timedelta(days=25)).isoformat()),
        ("REQ-2024-004", "Review Q4 budget allocations", user_map["fiona.green"], category_map["Finance & Accounting"], "High", (base_date - timedelta(days=20)).isoformat()),
        ("REQ-2024-005", "Implement REST API v2", user_map["eddie.murphy"], category_map["Feature Request"], "Medium", (base_date - timedelta(days=18)).isoformat()),
        ("REQ-2024-006", "Fix login page styling", user_map["george.harris"], category_map["Bug Report"], "Low", (base_date - timedelta(days=15)).isoformat()),
        ("REQ-2024-007", "Configure monitoring alerts", user_map["hannah.lee"], category_map["Infrastructure"], "High", (base_date - timedelta(days=12)).isoformat()),
        ("REQ-2024-008", "Upgrade PostgreSQL server", user_map["bob.johnson"], category_map["Infrastructure"], "Medium", (base_date - timedelta(days=10)).isoformat()),
        ("REQ-2024-009", "Create user documentation", user_map["alice.williams"], category_map["General Inquiry"], "Low", (base_date - timedelta(days=8)).isoformat()),
        ("REQ-2024-010", "Add two-factor authentication", user_map["eddie.murphy"], category_map["Feature Request"], "High", (base_date - timedelta(days=7)).isoformat()),
        ("REQ-2024-011", "Resolve API timeout issues", user_map["hannah.lee"], category_map["Technical Issue"], "High", (base_date - timedelta(days=5)).isoformat()),
        ("REQ-2024-012", "Optimize database queries", user_map["george.harris"], category_map["Technical Issue"], "Medium", (base_date - timedelta(days=4)).isoformat()),
        ("REQ-2024-013", "Add email notification system", user_map["charlie.brown"], category_map["Feature Request"], "Medium", (base_date - timedelta(days=3)).isoformat()),
        ("REQ-2024-014", "Fix mobile app crash on startup", user_map["fiona.green"], category_map["Bug Report"], "High", (base_date - timedelta(days=2)).isoformat()),
        ("REQ-2024-015", "Setup backup and disaster recovery", user_map["john.doe"], category_map["Infrastructure"], "High", (base_date - timedelta(days=1)).isoformat()),
        ("REQ-2024-016", "Implement search functionality", user_map["diana.prince"], category_map["Feature Request"], "Medium", base_date.isoformat()),
        ("REQ-2024-017", "Create API rate limiting", user_map["bob.johnson"], category_map["Technical Issue"], "Medium", base_date.isoformat()),
        ("REQ-2024-018", "Update security policies", user_map["jane.smith"], category_map["HR & Personnel"], "High", (base_date - timedelta(hours=12)).isoformat()),
        ("REQ-2024-019", "Audit financial transactions", user_map["alice.williams"], category_map["Finance & Accounting"], "Medium", (base_date - timedelta(hours=6)).isoformat()),
        ("REQ-2024-020", "Deploy to production", user_map["eddie.murphy"], category_map["Infrastructure"], "High", (base_date - timedelta(hours=3)).isoformat()),
    ]
    
    database.execute("DELETE FROM Requests")
    database.execute("DELETE FROM RequestHistory")
    
    cursor = database.executemany(
        "INSERT INTO Requests (request_number, description, applicant_user_id, category_id, priority, registered_at) VALUES (?, ?, ?, ?, ?, ?)",
        requests_data
    )
    print(f"✓ Loaded {cursor.rowcount} sample requests")
    
    # =========================================================================
    # 7. Load Request History (Initial Status)
    # =========================================================================
    # Get request IDs
    requests_result = database.execute(
        "SELECT request_id FROM Requests ORDER BY request_id"
    ).fetchall()
    request_ids = [rid for (rid,) in requests_result]
    
    # Create initial history entries with various statuses
    history_data = []
    status_cycle = ["Submitted", "In Progress", "Pending Review", "Approved", "Completed"]
    
    for idx, request_id in enumerate(request_ids):
        initial_status = status_cycle[idx % len(status_cycle)]
        actor_user = user_map["john.doe"]  # Admin user
        
        history_data.append((
            request_id,
            actor_user,
            None,  # previous_status_id
            status_map[initial_status],  # new_status_id
            (base_date - timedelta(days=30-idx)).isoformat(),  # occurred_at
            f"Initial status: {initial_status}",  # explanation
        ))
    
    cursor = database.executemany(
        "INSERT INTO RequestHistory (request_id, actor_user_id, previous_status_id, new_status_id, occurred_at, explanation) VALUES (?, ?, ?, ?, ?, ?)",
        history_data
    )
    print(f"✓ Loaded {cursor.rowcount} request history entries")
    
    # =========================================================================
    # 8. Load Sample Comments
    # =========================================================================
    comments_data = [
        (1, user_map["jane.smith"], "Database team is investigating the connectivity issue", 0, (base_date - timedelta(days=29)).isoformat()),
        (1, user_map["bob.johnson"], "Found the root cause - connection pool exhaustion", 1, (base_date - timedelta(days=27)).isoformat()),
        (2, user_map["alice.williams"], "Auth module development is 50% complete", 0, (base_date - timedelta(days=26)).isoformat()),
        (2, user_map["eddie.murphy"], "Ready for code review", 1, (base_date - timedelta(days=24)).isoformat()),
        (3, user_map["charlie.brown"], "HR team to provide updated content", 0, (base_date - timedelta(days=23)).isoformat()),
        (4, user_map["jane.smith"], "Finance review completed - approved", 0, (base_date - timedelta(days=19)).isoformat()),
        (5, user_map["diana.prince"], "API v2 design finalized, implementation starting", 0, (base_date - timedelta(days=17)).isoformat()),
        (6, user_map["george.harris"], "CSS refactoring completed", 1, (base_date - timedelta(days=14)).isoformat()),
        (7, user_map["hannah.lee"], "Monitoring setup in progress", 1, (base_date - timedelta(days=11)).isoformat()),
        (10, user_map["eddie.murphy"], "Integrating TOTP authentication", 0, (base_date - timedelta(days=6)).isoformat()),
        (11, user_map["hannah.lee"], "Identified N+1 query issues", 1, (base_date - timedelta(days=4)).isoformat()),
        (14, user_map["fiona.green"], "Critical app crash fixed in latest build", 0, (base_date - timedelta(days=1)).isoformat()),
        (15, user_map["bob.johnson"], "Backup system is now operational", 1, (base_date - timedelta(hours=12)).isoformat()),
    ]
    
    database.execute("DELETE FROM Comments")
    cursor = database.executemany(
        "INSERT INTO Comments (request_id, author_user_id, text, is_service, created_at) VALUES (?, ?, ?, ?, ?)",
        comments_data
    )
    print(f"✓ Loaded {cursor.rowcount} sample comments")
    
    database.commit()
    print("\n✅ Database seed data loaded successfully!")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Load seed data into the Request System database"
    )
    parser.add_argument(
        "--database",
        default="requests.db",
        help="Path to the database file (default: requests.db)"
    )
    parser.add_argument(
        "--reset-db",
        action="store_true",
        help="Reset database to default schema before loading seed data"
    )
    
    args = parser.parse_args()
    database_path = Path(args.database)
    
    try:
        # If reset-db flag is set, reinitialize from schema
        if args.reset_db:
            if database_path.exists():
                database_path.unlink()
                print(f"✓ Deleted existing database: {database_path}")
            
            schema_path = project_root / "docs" / "sql" / "schema.sql"
            if not schema_path.exists():
                print(f"❌ Schema file not found: {schema_path}", file=sys.stderr)
                return 1
            
            print(f"📝 Initializing database from schema: {schema_path}")
            db = SQLiteDatabase(str(database_path), str(schema_path))
            db.initialize()
        
        # Connect to database
        print(f"🔗 Connecting to database: {database_path}")
        connection = sqlite3.connect(str(database_path))
        connection.execute("PRAGMA foreign_keys = ON")
        
        # Load seed data
        print("📥 Loading seed data...")
        load_seed_data(connection)
        connection.close()
        
        return 0
        
    except PersistenceError as e:
        print(f"❌ Database error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
