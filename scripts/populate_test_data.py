#!/usr/bin/env python3
"""
Test data population script for the Request System.

Populates a fresh database with test data from populate_test_data.sql:
- 4 users (user_id 1-4)
- 4 categories (category_id 1-4)
- 6 statuses (status_id 1-6)
- 10 requests with realistic status transitions and history

Usage:
    python scripts/populate_test_data.py

Or use sqlite3 directly:
    sqlite3 request-system.db < scripts/populate_test_data.sql

Environment variables:
    REQUEST_SYSTEM_DB: Path to database file (default: request-system.db)

Safety:
    - Checks that database is empty before inserting
    - Aborts if any tables already contain data
    - Uses transactions for atomic operations
"""

import os
import sqlite3
from pathlib import Path


def get_database_path() -> Path:
    """Get database path from environment or use default."""
    db_path = os.environ.get("REQUEST_SYSTEM_DB", "request-system.db")
    return Path(db_path)


def get_sql_script_path() -> Path:
    """Get path to the SQL seed script."""
    return Path(__file__).parent / "populate_test_data.sql"


def database_is_empty(connection: sqlite3.Connection) -> bool:
    """Check if all main tables are empty."""
    cursor = connection.cursor()
    tables_to_check = ["Users", "Statuses", "Categories", "Requests", "RequestHistory"]
    
    for table in tables_to_check:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"❌ Table '{table}' already contains {count} rows")
            return False
    
    return True


def main() -> None:
    """Main entry point."""
    db_path = get_database_path()
    sql_script = get_sql_script_path()
    
    print(f"📁 Database path: {db_path}")
    print(f"📄 SQL script path: {sql_script}")
    
    if not db_path.exists():
        print("❌ Database file does not exist. Please initialize it first:")
        print("   python -m request_system list")
        print("   (This will auto-initialize the database)")
        return
    
    if not sql_script.exists():
        print(f"❌ SQL script not found: {sql_script}")
        return
    
    try:
        connection = sqlite3.connect(str(db_path))
        connection.execute("PRAGMA foreign_keys = ON")
        
        print("\n🔍 Checking if database is empty...")
        if not database_is_empty(connection):
            print("\n❌ Database already contains data. Aborting to prevent data loss.")
            print("   To reset: delete the database file and reinitialize:")
            print("   1. Delete request-system.db")
            print("   2. Run: python -m request_system list")
            print("   3. Run: python scripts/populate_test_data.py")
            connection.close()
            return
        
        print("✅ Database is empty, proceeding with insertion\n")
        
        # Read and execute SQL script
        sql_content = sql_script.read_text(encoding="utf-8")
        
        try:
            cursor = connection.cursor()
            cursor.executescript(sql_content)
            connection.commit()
            
            print("✅ All test data inserted successfully!")
            print("\n📊 Summary:")
            print("   • 4 users (user_id 1-4)")
            print("   • 4 categories (category_id 1-4)")
            print("   • 6 statuses (status_id 1-6)")
            print("   • 10 requests (request_id 1-10)")
            print("   • 24 history entries")
            
            print("\n🧪 To verify, run:")
            print("   python -m request_system list")
            print("   python -m request_system list --status \"В работе\"")
            print("   python -m request_system list --user 1")
            print("   python -m request_system get 1")
            
        except sqlite3.Error as error:
            connection.rollback()
            print(f"\n❌ Error during insertion: {error}")
            raise
        finally:
            connection.close()
    
    except sqlite3.Error as error:
        print(f"❌ Database error: {error}")
        raise


if __name__ == "__main__":
    main()
