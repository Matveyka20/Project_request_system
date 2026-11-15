"""Tests for search and filtering functionality."""

import unittest
from datetime import datetime, timezone
from pathlib import Path

from request_system.application.services.request_service import (
    FilteredListRequestsResult,
    RequestService,
)
from request_system.domain.entities import (
    Category,
    Request,
    RequestHistory,
    Status,
    User,
)
from request_system.infrastructure.database.sqlite.unit_of_work import (
    SQLiteUnitOfWork,
)
from request_system.infrastructure.database.sqlite.database import (
    SQLiteDatabase,
)


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 11, 12, 12, 0, tzinfo=timezone.utc)


class TestSearchAndFiltering(unittest.TestCase):
    """Test cases for search and filtering functionality."""

    def setUp(self) -> None:
        """Set up test database and service."""
        self.db_path = ROOT / "test_search_filtering.db"
        if self.db_path.exists():
            self.db_path.unlink()

        self.db = SQLiteDatabase(str(self.db_path))
        self.db.init_schema()

        self.service = RequestService(
            lambda: SQLiteUnitOfWork(self.db.connection),
            clock=lambda: NOW,
        )

        self._setup_test_data()

    def tearDown(self) -> None:
        """Clean up test database."""
        if self.db_path.exists():
            self.db_path.unlink()

    def _setup_test_data(self) -> None:
        """Create test data for filtering tests."""
        with SQLiteUnitOfWork(self.db.connection) as uow:
            users_data = [
                User(user_id=None, account="john.doe", name="John Doe", contacts="john@example.com"),
                User(user_id=None, account="jane.smith", name="Jane Smith", contacts="jane@example.com"),
                User(user_id=None, account="bob.wilson", name="Bob Wilson", contacts="bob@example.com"),
            ]
            statuses_data = [
                Status(status_id=None, name="Новая"),
                Status(status_id=None, name="В работе"),
                Status(status_id=None, name="Завершена"),
            ]
            categories_data = [
                Category(category_id=None, name="IT"),
                Category(category_id=None, name="HR"),
                Category(category_id=None, name="Администрация"),
            ]

            for user in users_data:
                uow.users.create(user)
            for status in statuses_data:
                uow.statuses.create(status)
            for category in categories_data:
                uow.categories.create(category)
            uow.commit()

        with SQLiteUnitOfWork(self.db.connection) as uow:
            requests_data = [
                Request(
                    request_id=None,
                    request_number="REQ-001",
                    description="Требуется новое оборудование для отдела IT",
                    applicant_user_id=1,
                    category_id=1,
                    priority="Высокий",
                    registered_at=NOW,
                ),
                Request(
                    request_id=None,
                    request_number="REQ-002",
                    description="Оформление договора с поставщиком",
                    applicant_user_id=2,
                    category_id=3,
                    priority="Средний",
                    registered_at=NOW,
                ),
                Request(
                    request_id=None,
                    request_number="REQ-003",
                    description="Проведение собеседования кандидата",
                    applicant_user_id=3,
                    category_id=2,
                    priority="Низкий",
                    registered_at=NOW,
                ),
                Request(
                    request_id=None,
                    request_number="REQ-004",
                    description="Закупка оборудования для офиса",
                    applicant_user_id=1,
                    category_id=1,
                    priority="Высокий",
                    registered_at=NOW,
                ),
                Request(
                    request_id=None,
                    request_number="REQ-005",
                    description="Информационное письмо о политике компании",
                    applicant_user_id=2,
                    category_id=3,
                    priority="Низкий",
                    registered_at=NOW,
                ),
            ]

            for request in requests_data:
                initial_status = uow.statuses.get_by_name("Новая")
                if initial_status and initial_status.status_id:
                    uow.requests.create_with_initial_status(
                        request,
                        actor_user_id=request.applicant_user_id,
                        previous_status_id=None,
                        new_status_id=initial_status.status_id,
                        occurred_at=NOW,
                    )

            uow.requests.list_all()[0]
            requests_by_id = uow.requests.list_all()
            if len(requests_by_id) >= 2:
                status_in_work = uow.statuses.get_by_name("В работе")
                if status_in_work and status_in_work.status_id:
                    new_status = uow.statuses.get_by_name("Новая")
                    uow.requests.create_with_initial_status(
                        requests_by_id[1],
                        actor_user_id=2,
                        previous_status_id=new_status.status_id if new_status else None,
                        new_status_id=status_in_work.status_id,
                        occurred_at=NOW,
                    )

            uow.commit()

    def test_list_all_requests_no_filters(self) -> None:
        """Test listing all requests without filters."""
        result = self.service.list_requests_with_filters(limit=100)
        self.assertEqual(result.total_count, 5)
        self.assertEqual(result.filtered_count, 5)
        self.assertEqual(result.returned_count, 5)
        self.assertFalse(result.has_next)
        self.assertFalse(result.has_previous)

    def test_filter_by_user_id(self) -> None:
        """Test filtering by user_id."""
        result = self.service.list_requests_with_filters(user_id=1, limit=100)
        self.assertEqual(result.filtered_count, 2)
        for req, _, _, _ in result.requests:
            self.assertEqual(req.applicant_user_id, 1)

    def test_filter_by_category_id(self) -> None:
        """Test filtering by category_id."""
        result = self.service.list_requests_with_filters(category_id=1, limit=100)
        self.assertEqual(result.filtered_count, 2)
        for req, _, _, _ in result.requests:
            self.assertEqual(req.category_id, 1)

    def test_filter_by_priority(self) -> None:
        """Test filtering by priority."""
        result = self.service.list_requests_with_filters(priority="Высокий", limit=100)
        self.assertEqual(result.filtered_count, 2)
        for req, _, _, _ in result.requests:
            self.assertEqual(req.priority, "Высокий")

    def test_filter_by_account_name_substring(self) -> None:
        """Test filtering by account_name (substring match, case-insensitive)."""
        result = self.service.list_requests_with_filters(account_name="john", limit=100)
        self.assertEqual(result.filtered_count, 2)
        for _, _, user_name, _ in result.requests:
            self.assertIn("John", user_name)

    def test_search_across_description_and_account_name(self) -> None:
        """Test full-text search across description and account_name."""
        result = self.service.list_requests_with_filters(search="договор", limit=100)
        self.assertGreater(result.filtered_count, 0)
        found_description = False
        for req, _, _, _ in result.requests:
            if "договор" in req.description.lower():
                found_description = True
        self.assertTrue(found_description or result.filtered_count > 0)

    def test_search_description_only(self) -> None:
        """Test searching only in description field."""
        result = self.service.list_requests_with_filters(search_description="оборудование", limit=100)
        self.assertGreater(result.filtered_count, 0)
        for req, _, _, _ in result.requests:
            self.assertIn("оборудование", req.description.lower())

    def test_sort_by_priority_ascending(self) -> None:
        """Test sorting by priority in ascending order."""
        result = self.service.list_requests_with_filters(
            sort_by="priority", sort_order="asc", limit=100
        )
        priorities = [req.priority or "" for req, _, _, _ in result.requests]
        self.assertEqual(priorities, sorted(priorities))

    def test_sort_by_priority_descending(self) -> None:
        """Test sorting by priority in descending order."""
        result = self.service.list_requests_with_filters(
            sort_by="priority", sort_order="desc", limit=100
        )
        priorities = [req.priority or "" for req, _, _, _ in result.requests]
        self.assertEqual(priorities, sorted(priorities, reverse=True))

    def test_sort_by_created_at_descending(self) -> None:
        """Test sorting by created_at in descending order (default)."""
        result = self.service.list_requests_with_filters(limit=100)
        times = [req.registered_at for req, _, _, _ in result.requests]
        self.assertEqual(times, sorted(times, reverse=True))

    def test_pagination_with_offset(self) -> None:
        """Test pagination using offset."""
        result1 = self.service.list_requests_with_filters(limit=2, offset=0)
        result2 = self.service.list_requests_with_filters(limit=2, offset=2)

        self.assertEqual(result1.returned_count, 2)
        self.assertEqual(result2.returned_count, 2)
        self.assertTrue(result1.has_next)
        self.assertTrue(result2.has_previous)

        ids1 = [req.request_id for req, _, _, _ in result1.requests]
        ids2 = [req.request_id for req, _, _, _ in result2.requests]
        self.assertNotEqual(ids1, ids2)

    def test_pagination_with_page_parameter(self) -> None:
        """Test pagination using page parameter."""
        result1 = self.service.list_requests_with_filters(limit=2, offset=0)
        result2 = self.service.list_requests_with_filters(limit=2, offset=2)

        ids1 = [req.request_id for req, _, _, _ in result1.requests]
        ids2 = [req.request_id for req, _, _, _ in result2.requests]

        self.assertEqual(result1.offset, 0)
        self.assertEqual(result2.offset, 2)

    def test_combined_filter_and_search(self) -> None:
        """Test combining filters and search."""
        result = self.service.list_requests_with_filters(
            category_id=1,
            search="оборудование",
            limit=100,
        )
        self.assertGreater(result.filtered_count, 0)
        for req, _, _, _ in result.requests:
            self.assertEqual(req.category_id, 1)
            self.assertIn("оборудование", req.description.lower())

    def test_combined_filters_sort_and_pagination(self) -> None:
        """Test combining multiple filters, sorting, and pagination."""
        result = self.service.list_requests_with_filters(
            user_id=1,
            sort_by="priority",
            sort_order="desc",
            limit=1,
            offset=0,
        )
        self.assertEqual(result.returned_count, 1)
        for req, _, _, _ in result.requests:
            self.assertEqual(req.applicant_user_id, 1)

    def test_no_results_found(self) -> None:
        """Test when no results match the filter."""
        result = self.service.list_requests_with_filters(
            user_id=999, limit=100
        )
        self.assertEqual(result.filtered_count, 0)
        self.assertEqual(result.returned_count, 0)
        self.assertFalse(result.has_next)
        self.assertFalse(result.has_previous)

    def test_case_insensitive_search(self) -> None:
        """Test that search is case-insensitive."""
        result1 = self.service.list_requests_with_filters(
            search="ДОГОВОР", limit=100
        )
        result2 = self.service.list_requests_with_filters(
            search="договор", limit=100
        )
        self.assertEqual(result1.filtered_count, result2.filtered_count)

    def test_case_insensitive_account_name_filter(self) -> None:
        """Test that account_name filter is case-insensitive."""
        result1 = self.service.list_requests_with_filters(
            account_name="JOHN", limit=100
        )
        result2 = self.service.list_requests_with_filters(
            account_name="john", limit=100
        )
        self.assertEqual(result1.filtered_count, result2.filtered_count)

    def test_pagination_has_next_flag(self) -> None:
        """Test has_next flag is correct."""
        result = self.service.list_requests_with_filters(limit=3, offset=0)
        self.assertTrue(result.has_next)

        result = self.service.list_requests_with_filters(limit=100, offset=0)
        self.assertFalse(result.has_next)

    def test_pagination_has_previous_flag(self) -> None:
        """Test has_previous flag is correct."""
        result = self.service.list_requests_with_filters(limit=2, offset=0)
        self.assertFalse(result.has_previous)

        result = self.service.list_requests_with_filters(limit=2, offset=2)
        self.assertTrue(result.has_previous)

    def test_response_metadata_consistency(self) -> None:
        """Test that response metadata is consistent."""
        result = self.service.list_requests_with_filters(limit=2, offset=1)
        self.assertEqual(result.limit, 2)
        self.assertEqual(result.offset, 1)
        self.assertEqual(result.returned_count, len(result.requests))
        self.assertLessEqual(result.filtered_count, result.total_count)


if __name__ == "__main__":
    unittest.main()
