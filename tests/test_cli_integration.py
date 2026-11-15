"""Integration tests for CLI commands."""

from io import StringIO
import os
from pathlib import Path
import tempfile
from unittest import TestCase
from unittest.mock import patch
from click.testing import CliRunner

from request_system.application.services.request_service import RequestService
from request_system.domain.entities import Category, Status, User
from request_system.infrastructure.database.sqlite import SQLiteDatabase
from request_system.presentation.cli_commands import cli

ROOT = Path(__file__).resolve().parents[1]


class CliIntegrationTests(TestCase):
    """Integration tests for CLI commands using real SQLite database."""

    def setUp(self) -> None:
        """Set up a temporary database for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test.db"
        self.database = SQLiteDatabase(
            self.database_path,
            ROOT / "docs" / "sql" / "schema.sql",
        )
        self.database.initialize()

        # Seed database with test data
        with self.database.unit_of_work() as uow:
            self.user1 = uow.users.add(User(None, "testuser1", "Test User 1"))
            self.user2 = uow.users.add(User(None, "testuser2", "Test User 2"))
            self.category1 = uow.categories.add(Category(None, "bug"))
            self.category2 = uow.categories.add(Category(None, "feature"))
            self.status_new = uow.statuses.add(Status(None, "Новая"))
            self.status_in_progress = uow.statuses.add(Status(None, "В обработке"))
            self.status_closed = uow.statuses.add(Status(None, "Закрыта"))

    def tearDown(self) -> None:
        """Clean up the temporary database."""
        self.temp_dir.cleanup()

    def _run_cli(self, *args: str) -> tuple[int, str]:
        """Run CLI command and return exit code and output."""
        runner = CliRunner()
        service = RequestService(self.database.unit_of_work)

        from request_system.presentation.cli_commands import CliContext
        result = runner.invoke(
            cli,
            args,
            obj=CliContext(service),
        )

        return result.exit_code, result.output

    def test_create_request_happy_path(self) -> None:
        """Test creating a request successfully."""
        exit_code, output = self._run_cli(
            "create",
            "--user", str(self.user1.user_id),
            "--category", str(self.category1.category_id),
            "--description", "Test request",
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("Заявка создана", output)
        self.assertIn("ID:", output)
        self.assertIn("Статус: Новая", output)

        # Verify request was persisted
        with self.database.unit_of_work() as uow:
            requests = uow.requests.list_all()
            self.assertEqual(len(requests), 1)
            self.assertEqual(requests[0].description, "Test request")

    def test_create_request_validation_error(self) -> None:
        """Test creating a request with invalid user."""
        exit_code, output = self._run_cli(
            "create",
            "--user", "9999",
            "--category", str(self.category1.category_id),
            "--description", "Test request",
        )

        self.assertEqual(exit_code, 2)
        self.assertIn("Ошибка:", output)
        self.assertIn("не найден", output)

    def test_get_request_happy_path(self) -> None:
        """Test getting a request by ID."""
        # First create a request
        with self.database.unit_of_work() as uow:
            initial_status = uow.statuses.get_by_name("Новая")
            request, _ = uow.requests.create_with_initial_status(
                __import__("request_system.domain.entities", fromlist=["Request"]).Request(
                    request_id=None,
                    request_number="REQ-001",
                    description="Test request",
                    applicant_user_id=self.user1.user_id,
                    category_id=self.category1.category_id,
                    priority=None,
                    registered_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
                ),
                actor_user_id=self.user1.user_id,
                previous_status_id=None,
                new_status_id=initial_status.status_id,
                occurred_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            )

        exit_code, output = self._run_cli(
            "get",
            str(request.request_id),
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("ID:", output)
        self.assertIn("Номер: REQ-001", output)
        self.assertIn("Заявитель: Test User 1", output)
        self.assertIn("Категория: bug", output)
        self.assertIn("Описание: Test request", output)
        self.assertIn("Статус: Новая", output)

    def test_get_request_not_found(self) -> None:
        """Test getting a non-existent request."""
        exit_code, output = self._run_cli(
            "get",
            "9999",
        )

        self.assertEqual(exit_code, 2)
        self.assertIn("Ошибка:", output)
        self.assertIn("не найдена", output)

    def test_list_requests_empty(self) -> None:
        """Test listing requests when none exist."""
        exit_code, output = self._run_cli("list")

        self.assertEqual(exit_code, 0)
        self.assertIn("Нет заявок", output)

    def test_list_requests_with_data(self) -> None:
        """Test listing requests with data."""
        # Create a request
        with self.database.unit_of_work() as uow:
            initial_status = uow.statuses.get_by_name("Новая")
            from datetime import datetime, timezone
            from request_system.domain.entities import Request
            uow.requests.create_with_initial_status(
                Request(
                    request_id=None,
                    request_number="REQ-001",
                    description="Test request",
                    applicant_user_id=self.user1.user_id,
                    category_id=self.category1.category_id,
                    priority=None,
                    registered_at=datetime.now(timezone.utc),
                ),
                actor_user_id=self.user1.user_id,
                previous_status_id=None,
                new_status_id=initial_status.status_id,
                occurred_at=datetime.now(timezone.utc),
            )

        exit_code, output = self._run_cli("list")

        self.assertEqual(exit_code, 0)
        self.assertIn("ID", output)
        self.assertIn("Пользователь", output)
        self.assertIn("Категория", output)
        self.assertIn("Статус", output)
        self.assertIn("Test User 1", output)
        self.assertIn("bug", output)

    def test_list_requests_filter_by_user(self) -> None:
        """Test listing requests filtered by user."""
        # Create requests for different users
        with self.database.unit_of_work() as uow:
            initial_status = uow.statuses.get_by_name("Новая")
            from datetime import datetime, timezone
            from request_system.domain.entities import Request
            uow.requests.create_with_initial_status(
                Request(
                    request_id=None,
                    request_number="REQ-001",
                    description="User1 request",
                    applicant_user_id=self.user1.user_id,
                    category_id=self.category1.category_id,
                    priority=None,
                    registered_at=datetime.now(timezone.utc),
                ),
                actor_user_id=self.user1.user_id,
                previous_status_id=None,
                new_status_id=initial_status.status_id,
                occurred_at=datetime.now(timezone.utc),
            )
            uow.requests.create_with_initial_status(
                Request(
                    request_id=None,
                    request_number="REQ-002",
                    description="User2 request",
                    applicant_user_id=self.user2.user_id,
                    category_id=self.category1.category_id,
                    priority=None,
                    registered_at=datetime.now(timezone.utc),
                ),
                actor_user_id=self.user2.user_id,
                previous_status_id=None,
                new_status_id=initial_status.status_id,
                occurred_at=datetime.now(timezone.utc),
            )

        exit_code, output = self._run_cli(
            "list",
            "--user", str(self.user1.user_id),
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("Test User 1", output)
        self.assertNotIn("Test User 2", output)

    def test_update_request_happy_path(self) -> None:
        """Test updating a request's description."""
        # Create a request
        with self.database.unit_of_work() as uow:
            initial_status = uow.statuses.get_by_name("Новая")
            from datetime import datetime, timezone
            from request_system.domain.entities import Request
            request, _ = uow.requests.create_with_initial_status(
                Request(
                    request_id=None,
                    request_number="REQ-001",
                    description="Original description",
                    applicant_user_id=self.user1.user_id,
                    category_id=self.category1.category_id,
                    priority=None,
                    registered_at=datetime.now(timezone.utc),
                ),
                actor_user_id=self.user1.user_id,
                previous_status_id=None,
                new_status_id=initial_status.status_id,
                occurred_at=datetime.now(timezone.utc),
            )

        exit_code, output = self._run_cli(
            "update",
            str(request.request_id),
            "--description", "Updated description",
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("Заявка обновлена", output)
        self.assertIn("Updated description", output)

        # Verify update was persisted
        with self.database.unit_of_work() as uow:
            updated_request = uow.requests.get(request.request_id)
            self.assertEqual(updated_request.description, "Updated description")

    def test_update_request_wrong_status(self) -> None:
        """Test updating a request that's not in 'Новая' status."""
        # Create a request in 'В обработке' status
        with self.database.unit_of_work() as uow:
            new_status = uow.statuses.get_by_name("Новая")
            in_progress_status = uow.statuses.get_by_name("В обработке")
            from datetime import datetime, timezone
            from request_system.domain.entities import Request
            request, _ = uow.requests.create_with_initial_status(
                Request(
                    request_id=None,
                    request_number="REQ-001",
                    description="Original description",
                    applicant_user_id=self.user1.user_id,
                    category_id=self.category1.category_id,
                    priority=None,
                    registered_at=datetime.now(timezone.utc),
                ),
                actor_user_id=self.user1.user_id,
                previous_status_id=None,
                new_status_id=new_status.status_id,
                occurred_at=datetime.now(timezone.utc),
            )
            # Change to in-progress
            uow.requests.create_with_initial_status(
                request,
                actor_user_id=self.user1.user_id,
                previous_status_id=new_status.status_id,
                new_status_id=in_progress_status.status_id,
                occurred_at=datetime.now(timezone.utc),
            )

        exit_code, output = self._run_cli(
            "update",
            str(request.request_id),
            "--description", "Updated description",
        )

        self.assertEqual(exit_code, 2)
        self.assertIn("Ошибка:", output)
        self.assertIn("нельзя редактировать", output.lower())

    def test_status_change_happy_path(self) -> None:
        """Test changing request status."""
        # Create a request
        with self.database.unit_of_work() as uow:
            initial_status = uow.statuses.get_by_name("Новая")
            from datetime import datetime, timezone
            from request_system.domain.entities import Request
            request, _ = uow.requests.create_with_initial_status(
                Request(
                    request_id=None,
                    request_number="REQ-001",
                    description="Test request",
                    applicant_user_id=self.user1.user_id,
                    category_id=self.category1.category_id,
                    priority=None,
                    registered_at=datetime.now(timezone.utc),
                ),
                actor_user_id=self.user1.user_id,
                previous_status_id=None,
                new_status_id=initial_status.status_id,
                occurred_at=datetime.now(timezone.utc),
            )

        exit_code, output = self._run_cli(
            "status",
            str(request.request_id),
            "--new-status", "В обработке",
            "--actor", str(self.user1.user_id),
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("Статус изменен", output)
        self.assertIn("Старый статус: Новая", output)
        self.assertIn("Новый статус: В обработке", output)

    def test_status_change_same_status(self) -> None:
        """Test changing request to same status."""
        # Create a request
        with self.database.unit_of_work() as uow:
            initial_status = uow.statuses.get_by_name("Новая")
            from datetime import datetime, timezone
            from request_system.domain.entities import Request
            request, _ = uow.requests.create_with_initial_status(
                Request(
                    request_id=None,
                    request_number="REQ-001",
                    description="Test request",
                    applicant_user_id=self.user1.user_id,
                    category_id=self.category1.category_id,
                    priority=None,
                    registered_at=datetime.now(timezone.utc),
                ),
                actor_user_id=self.user1.user_id,
                previous_status_id=None,
                new_status_id=initial_status.status_id,
                occurred_at=datetime.now(timezone.utc),
            )

        exit_code, output = self._run_cli(
            "status",
            str(request.request_id),
            "--new-status", "Новая",
            "--actor", str(self.user1.user_id),
        )

        self.assertEqual(exit_code, 2)
        self.assertIn("Ошибка:", output)

    def test_status_change_nonexistent_status(self) -> None:
        """Test changing request to non-existent status."""
        # Create a request
        with self.database.unit_of_work() as uow:
            initial_status = uow.statuses.get_by_name("Новая")
            from datetime import datetime, timezone
            from request_system.domain.entities import Request
            request, _ = uow.requests.create_with_initial_status(
                Request(
                    request_id=None,
                    request_number="REQ-001",
                    description="Test request",
                    applicant_user_id=self.user1.user_id,
                    category_id=self.category1.category_id,
                    priority=None,
                    registered_at=datetime.now(timezone.utc),
                ),
                actor_user_id=self.user1.user_id,
                previous_status_id=None,
                new_status_id=initial_status.status_id,
                occurred_at=datetime.now(timezone.utc),
            )

        exit_code, output = self._run_cli(
            "status",
            str(request.request_id),
            "--new-status", "NonExistent",
            "--actor", str(self.user1.user_id),
        )

        self.assertEqual(exit_code, 2)
        self.assertIn("Ошибка:", output)
