"""Manual API verification without running uvicorn server."""

import sys
import os
from pathlib import Path

# Change to project root
os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Now import
try:
    from request_system.infrastructure.database.sqlite import SQLiteDatabase
    from request_system.infrastructure.database.sqlite.unit_of_work import SQLiteUnitOfWork
    from request_system.application.services.request_service import (
        RequestService,
        CreateRequestCommand,
    )
    from request_system.domain.entities import User, Status, Category
    from datetime import datetime, timezone

    print("✓ All imports successful!")
    
    # Setup
    db_file = Path("verify_test.db")
    if db_file.exists():
        db_file.unlink()
    
    db = SQLiteDatabase(str(db_file))
    db.init_schema()
    print("✓ Database initialized")
    
    # Add test data
    with SQLiteUnitOfWork(db.connection) as uow:
        for user in [
            User(user_id=None, account="john.doe", name="John Doe", contacts="john@example.com"),
            User(user_id=None, account="jane.smith", name="Jane Smith", contacts="jane@example.com"),
            User(user_id=None, account="bob.wilson", name="Bob Wilson", contacts="bob@example.com"),
        ]:
            uow.users.create(user)
        
        for status in [
            Status(status_id=None, name="Новая"),
            Status(status_id=None, name="В работе"),
            Status(status_id=None, name="Завершена"),
        ]:
            uow.statuses.create(status)
        
        for cat in [
            Category(category_id=None, name="IT"),
            Category(category_id=None, name="HR"),
            Category(category_id=None, name="Администрация"),
        ]:
            uow.categories.create(cat)
        
        uow.commit()
    print("✓ Test users, statuses, categories created")
    
    # Register requests
    service = RequestService(lambda: SQLiteUnitOfWork(db.connection))
    test_requests = [
        ("Требуется новое оборудование для отдела IT", 1, 1, "Высокий"),
        ("Оформление договора с поставщиком", 2, 3, "Средний"),
        ("Проведение собеседования кандидата", 3, 2, "Низкий"),
        ("Закупка оборудования для офиса", 1, 1, "Высокий"),
        ("Информационное письмо о политике компании", 2, 3, "Низкий"),
        ("Техническое обслуживание серверов", 1, 1, "Высокий"),
        ("Подготовка договора аренды", 3, 3, "Средний"),
    ]
    
    for desc, uid, cid, pri in test_requests:
        service.register(CreateRequestCommand(
            applicant_user_id=uid,
            description=desc,
            category_id=cid,
        ))
    print(f"✓ {len(test_requests)} test requests registered")
    
    # Run tests
    tests = [
        ("1. List all requests", {}),
        ("2. Filter by user_id=1", {"user_id": 1}),
        ("3. Filter by status='Новая'", {"status": "Новая"}),
        ("4. Filter by priority='Высокий'", {"priority": "Высокий"}),
        ("5. Filter by category_id=1", {"category_id": 1}),
        ("6. FullText search 'договор'", {"search": "договор"}),
        ("7. Description search 'оборудование'", {"search_description": "оборудование"}),
        ("8. Sort by priority DESC", {"sort_by": "priority", "sort_order": "desc", "limit": 100}),
        ("9. Sort by id ASC", {"sort_by": "id", "sort_order": "asc", "limit": 100}),
        ("10. Pagination limit=3 offset=0", {"limit": 3, "offset": 0}),
        ("11. Pagination limit=3 page=2", {"limit": 3, "page": 2}),
        ("12. Filter user_id=1 + sort", {"user_id": 1, "sort_by": "created_at", "sort_order": "desc", "limit": 5}),
        ("13. Filter account_name 'john'", {"account_name": "john"}),
    ]
    
    print("\n" + "="*80)
    print("RUNNING API VERIFICATION TESTS")
    print("="*80 + "\n")
    
    passed = 0
    failed = 0
    
    for test_name, params in tests:
        try:
            result = service.list_requests_with_filters(**params)
            
            # Verify structure
            assert hasattr(result, 'requests'), "Missing 'requests'"
            assert hasattr(result, 'total_count'), "Missing 'total_count'"
            assert hasattr(result, 'filtered_count'), "Missing 'filtered_count'"
            assert hasattr(result, 'returned_count'), "Missing 'returned_count'"
            assert hasattr(result, 'has_next'), "Missing 'has_next'"
            assert hasattr(result, 'has_previous'), "Missing 'has_previous'"
            
            # Verify logic
            assert result.returned_count <= result.filtered_count, "returned_count > filtered_count"
            assert result.filtered_count <= result.total_count, "filtered_count > total_count"
            
            print(f"✓ {test_name}")
            print(f"  Total: {result.total_count}, Filtered: {result.filtered_count}, " + 
                  f"Returned: {result.returned_count}, Next: {result.has_next}, Prev: {result.has_previous}")
            passed += 1
        except Exception as e:
            print(f"✗ {test_name}")
            print(f"  ERROR: {str(e)[:100]}")
            failed += 1
        print()
    
    print("="*80)
    print(f"RESULTS: {passed} PASSED, {failed} FAILED")
    print("="*80)
    
except Exception as e:
    print(f"FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
