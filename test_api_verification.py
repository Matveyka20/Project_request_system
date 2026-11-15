#!/usr/bin/env python3
"""Test script to verify API functionality without running a server."""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from request_system.infrastructure.database.sqlite import SQLiteDatabase
from request_system.infrastructure.database.sqlite.unit_of_work import SQLiteUnitOfWork
from request_system.application.services.request_service import RequestService, CreateRequestCommand
from request_system.domain.entities import User, Status, Category

def setup_test_data():
    """Create test database with sample data."""
    db_path = Path(__file__).parent / "test_api.db"
    if db_path.exists():
        db_path.unlink()
    
    db = SQLiteDatabase(str(db_path))
    db.init_schema()
    
    # Add test data
    with SQLiteUnitOfWork(db.connection) as uow:
        # Create users
        users = [
            User(user_id=None, account="john.doe", name="John Doe", contacts="john@example.com"),
            User(user_id=None, account="jane.smith", name="Jane Smith", contacts="jane@example.com"),
            User(user_id=None, account="bob.wilson", name="Bob Wilson", contacts="bob@example.com"),
            User(user_id=None, account="alice.johnson", name="Alice Johnson", contacts="alice@example.com"),
        ]
        for user in users:
            uow.users.create(user)
        
        # Create statuses
        statuses = [
            Status(status_id=None, name="Новая"),
            Status(status_id=None, name="В работе"),
            Status(status_id=None, name="Завершена"),
        ]
        for status in statuses:
            uow.statuses.create(status)
        
        # Create categories
        categories = [
            Category(category_id=None, name="IT"),
            Category(category_id=None, name="HR"),
            Category(category_id=None, name="Администрация"),
        ]
        for category in categories:
            uow.categories.create(category)
        
        uow.commit()
    
    # Register requests
    service = RequestService(lambda: SQLiteUnitOfWork(db.connection))
    
    requests_data = [
        ("Требуется новое оборудование для отдела IT", 1, 1, "Высокий"),
        ("Оформление договора с поставщиком", 2, 3, "Средний"),
        ("Проведение собеседования кандидата", 3, 2, "Низкий"),
        ("Закупка оборудования для офиса", 1, 1, "Высокий"),
        ("Информационное письмо о политике компании", 2, 3, "Низкий"),
        ("Техническое обслуживание серверов", 1, 1, "Высокий"),
        ("Подготовка договора аренды", 4, 3, "Средний"),
    ]
    
    for description, user_id, category_id, priority in requests_data:
        try:
            result = service.register(CreateRequestCommand(
                applicant_user_id=user_id,
                description=description,
                category_id=category_id,
            ))
        except Exception as e:
            print(f"Error registering request: {e}")
    
    return db

def test_api(db):
    """Run test queries."""
    service = RequestService(lambda: SQLiteUnitOfWork(db.connection))
    
    tests = [
        ("List all requests", {}),
        ("Filter by user_id=1", {"user_id": 1}),
        ("Filter by status='Новая'", {"status": "Новая"}),
        ("Filter by priority='Высокий'", {"priority": "Высокий"}),
        ("Filter by category_id=1", {"category_id": 1}),
        ("FullText search 'договор'", {"search": "договор"}),
        ("Description search 'оборудование'", {"search_description": "оборудование"}),
        ("Sort by priority DESC", {"sort_by": "priority", "sort_order": "desc", "limit": 100}),
        ("Sort by id ASC", {"sort_by": "id", "sort_order": "asc", "limit": 100}),
        ("Pagination limit=3 offset=0", {"limit": 3, "offset": 0}),
        ("Pagination limit=3 page=2 (offset=3)", {"limit": 3, "offset": 3}),
        ("Filter user_id=1 + sort + pagination", {"user_id": 1, "sort_by": "created_at", "sort_order": "desc", "limit": 5}),
        ("Filter account_name 'john'", {"account_name": "john"}),
    ]
    
    results = []
    for test_name, params in tests:
        try:
            result = service.list_requests_with_filters(**params)
            
            test_result = {
                "test": test_name,
                "status": "✓ PASS",
                "total_count": result.total_count,
                "filtered_count": result.filtered_count,
                "returned_count": result.returned_count,
                "limit": result.limit,
                "offset": result.offset,
                "has_next": result.has_next,
                "has_previous": result.has_previous,
                "params": params,
            }
            
            # Verify response structure
            if (result.total_count >= 0 and result.filtered_count >= 0 and 
                result.returned_count >= 0 and result.returned_count <= result.filtered_count):
                results.append(test_result)
            else:
                test_result["status"] = "✗ FAIL - Invalid counts"
                results.append(test_result)
        except Exception as e:
            results.append({
                "test": test_name,
                "status": f"✗ ERROR: {str(e)}",
                "params": params,
            })
    
    return results

def print_results(results):
    """Print test results."""
    print("\n" + "="*80)
    print("API VERIFICATION TEST RESULTS")
    print("="*80 + "\n")
    
    passed = 0
    failed = 0
    
    for i, result in enumerate(results, 1):
        status_icon = "✓" if "PASS" in result.get("status", "") else "✗"
        print(f"{i:2}. {status_icon} {result['test']}")
        print(f"    Status: {result['status']}")
        
        if "PASS" in result.get("status", ""):
            print(f"    Results: total={result['total_count']}, filtered={result['filtered_count']}, returned={result['returned_count']}")
            print(f"    Pagination: limit={result['limit']}, offset={result['offset']}, has_next={result['has_next']}, has_previous={result['has_previous']}")
            passed += 1
        else:
            failed += 1
        
        print()
    
    print("="*80)
    print(f"SUMMARY: {passed} PASSED, {failed} FAILED out of {len(results)} tests")
    print("="*80 + "\n")
    
    return passed, failed

if __name__ == "__main__":
    print("Setting up test database...")
    db = setup_test_data()
    
    print("Running API verification tests...\n")
    results = test_api(db)
    
    passed, failed = print_results(results)
    
    sys.exit(0 if failed == 0 else 1)
