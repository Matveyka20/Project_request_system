"""Comprehensive tests for CLI error handling and validation."""

import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock

from click.testing import CliRunner

from request_system.application.services.request_service import (
    CannotUpdateRequestError,
    InitialStatusNotConfigured,
    InvalidStatusTransitionError,
    RequestNotFoundError,
    RequestService,
    RequestValidationError,
    StatusNotFoundError,
    CreateRequestCommand,
)
from request_system.application.ports.persistence import PersistenceError
from request_system.domain.entities import Category, Status, User
from request_system.infrastructure.database.sqlite import SQLiteDatabase
from request_system.presentation.cli_commands import cli, CliContext

ROOT = Path(__file__).resolve().parents[1]


class CliErrorHandlingTests(TestCase):
    """Test CLI error handling and validation."""

    def setUp(self) -> None:
        """Set up test database and CLI."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.sqlite3"
        
        self.database = SQLiteDatabase(
            self.db_path,
            ROOT / "docs" / "sql" / "schema.sql",
        )
        self.database.initialize()
        
        # Create test data
        with self.database.unit_of_work() as uow:
            self.user = uow.users.add(User(None, "test_user", "Test User"))
            self.category = uow.categories.add(Category(None, "test_category"))
            self.status_new = uow.statuses.add(Status(None, "Новая"))
            self.status_pending = uow.statuses.add(Status(None, "В обработке"))
        
        self.service = RequestService(lambda: self.database.unit_of_work())
        self.runner = CliRunner(mix_stderr=False)

    def tearDown(self) -> None:
        """Clean up temp directory."""
        self.temp_dir.cleanup()

    # ========== Negative ID Tests ==========

    def test_create_with_negative_user_id(self) -> None:
        """Test create command with negative user ID."""
        result = self.runner.invoke(
            cli,
            ["create", "--user", "-1", "--category", "1", "--description", "test"],
            obj=CliContext(self.service),
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIn("положительным", result.output.lower())

    def test_create_with_zero_user_id(self) -> None:
        """Test create command with zero user ID."""
        result = self.runner.invoke(
            cli,
            ["create", "--user", "0", "--category", "1", "--description", "test"],
            obj=CliContext(self.service),
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIn("положительным", result.output.lower())

    def test_create_with_negative_category_id(self) -> None:
        """Test create command with negative category ID."""
        result = self.runner.invoke(
            cli,
            ["create", "--user", "1", "--category", "-5", "--description", "test"],
            obj=CliContext(self.service),
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIn("положительным", result.output.lower())

    def test_get_with_negative_request_id(self) -> None:
        """Test get command with negative request ID."""
        result = self.runner.invoke(
            cli,
            ["get", "-10"],
            obj=CliContext(self.service),
        )
        self.assertEqual(result.exit_code, 2)

    def test_update_with_zero_request_id(self) -> None:
        """Test update command with zero request ID."""
        result = self.runner.invoke(
            cli,
            ["update", "0", "--description", "new description"],
            obj=CliContext(self.service),
        )
        self.assertEqual(result.exit_code, 2)

    def test_status_with_negative_request_id(self) -> None:
        """Test status command with negative request ID."""
        result = self.runner.invoke(
            cli,
            ["status", "-1", "--new-status", "В обработке", "--actor", "1"],
            obj=CliContext(self.service),
        )
        self.assertEqual(result.exit_code, 2)

    def test_status_with_zero_actor_id(self) -> None:
        """Test status command with zero actor ID."""
        result = self.runner.invoke(
            cli,
            ["status", "1", "--new-status", "В обработке", "--actor", "0"],
            obj=CliContext(self.service),
        )
        self.assertEqual(result.exit_code, 2)

    # ========== Empty/Whitespace String Tests ==========

    def test_create_with_empty_description(self) -> None:
        """Test create command with empty description."""
        result = self.runner.invoke(
            cli,
            ["create", "--user", "1", "--category", "1", "--description", ""],
            obj=CliContext(self.service),
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIn("пусто", result.output.lower())

    def test_create_with_whitespace_only_description(self) -> None:
        """Test create command with whitespace-only description."""
        result = self.runner.invoke(
            cli,
            ["create", "--user", "1", "--category", "1", "--description", "   "],
            obj=CliContext(self.service),
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIn("пусто", result.output.lower())

    def test_update_with_empty_description(self) -> None:
        """Test update command with empty description."""
        result = self.runner.invoke(
            cli,
            ["update", "1", "--description", ""],
            obj=CliContext(self.service),
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIn("пусто", result.output.lower())

    # ========== Description Length Tests ==========

    def test_create_with_very_long_description(self) -> None:
        """Test create command with description exceeding max length."""
        long_desc = "x" * 1001
        result = self.runner.invoke(
            cli,
            ["create", "--user", "1", "--category", "1", "--description", long_desc],
            obj=CliContext(self.service),
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIn("слишком длинн", result.output.lower())

    def test_update_with_very_long_description(self) -> None:
        """Test update command with description exceeding max length."""
        long_desc = "x" * 1500
        result = self.runner.invoke(
            cli,
            ["update", "1", "--description", long_desc],
            obj=CliContext(self.service),
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIn("слишком длинн", result.output.lower())

    # ========== Exit Code Tests ==========

    def test_not_found_error_exit_code_2(self) -> None:
        """Test that NotFoundError returns exit code 2."""
        mock_service = MagicMock()
        mock_service.get_request.side_effect = RequestNotFoundError(999)
        
        result = self.runner.invoke(
            cli,
            ["get", "999"],
            obj=CliContext(mock_service),
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIn("не найдена", result.output.lower())

    def test_validation_error_exit_code_2(self) -> None:
        """Test that RequestValidationError returns exit code 2."""
        mock_service = MagicMock()
        mock_service.register.side_effect = RequestValidationError(
            {"description": "Укажите описание заявки."}
        )
        
        result = self.runner.invoke(
            cli,
            ["create", "--user", "1", "--category", "1", "--description", "test"],
            obj=CliContext(mock_service),
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIn("ошибка", result.output.lower())

    def test_invalid_status_transition_exit_code_2(self) -> None:
        """Test that InvalidStatusTransitionError returns exit code 2."""
        mock_service = MagicMock()
        mock_service.get_request.return_value = MagicMock(status=MagicMock(name="Новая"))
        mock_service.change_status.side_effect = InvalidStatusTransitionError(
            "Новая", "Завершена"
        )
        
        result = self.runner.invoke(
            cli,
            ["status", "1", "--new-status", "Завершена", "--actor", "1"],
            obj=CliContext(mock_service),
        )
        self.assertEqual(result.exit_code, 2)

    def test_cannot_update_request_error_exit_code_2(self) -> None:
        """Test that CannotUpdateRequestError returns exit code 2."""
        mock_service = MagicMock()
        mock_service.update_request_description.side_effect = CannotUpdateRequestError(
            1, "В обработке"
        )
        
        result = self.runner.invoke(
            cli,
            ["update", "1", "--description", "new"],
            obj=CliContext(mock_service),
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIn("статус", result.output.lower())

    def test_persistence_error_exit_code_3(self) -> None:
        """Test that PersistenceError returns exit code 3."""
        mock_service = MagicMock()
        mock_service.register.side_effect = PersistenceError()
        
        result = self.runner.invoke(
            cli,
            ["create", "--user", "1", "--category", "1", "--description", "test"],
            obj=CliContext(mock_service),
        )
        self.assertEqual(result.exit_code, 3)
        self.assertIn("сохранени", result.output.lower())

    def test_initial_status_not_configured_exit_code_3(self) -> None:
        """Test that InitialStatusNotConfigured returns exit code 3."""
        mock_service = MagicMock()
        mock_service.register.side_effect = InitialStatusNotConfigured()
        
        result = self.runner.invoke(
            cli,
            ["create", "--user", "1", "--category", "1", "--description", "test"],
            obj=CliContext(mock_service),
        )
        self.assertEqual(result.exit_code, 3)

    def test_unexpected_error_exit_code_1(self) -> None:
        """Test that unexpected errors return exit code 1."""
        mock_service = MagicMock()
        mock_service.get_request.side_effect = RuntimeError("Something went wrong")
        
        result = self.runner.invoke(
            cli,
            ["get", "1"],
            obj=CliContext(mock_service),
        )
        self.assertEqual(result.exit_code, 1)
        self.assertIn("внутренняя ошибка", result.output.lower())

    # ========== No Stack Trace Tests ==========

    def test_no_stack_trace_for_validation_error(self) -> None:
        """Test that validation errors don't show stack traces."""
        result = self.runner.invoke(
            cli,
            ["create", "--user", "-1", "--category", "1", "--description", "test"],
            obj=CliContext(self.service),
        )
        self.assertEqual(result.exit_code, 2)
        self.assertNotIn("Traceback", result.output)

    def test_no_stack_trace_for_not_found_error(self) -> None:
        """Test that not found errors don't show stack traces."""
        mock_service = MagicMock()
        mock_service.get_request.side_effect = RequestNotFoundError(999)
        
        result = self.runner.invoke(
            cli,
            ["get", "999"],
            obj=CliContext(mock_service),
        )
        self.assertEqual(result.exit_code, 2)
        self.assertNotIn("Traceback", result.output)

    def test_no_stack_trace_for_persistence_error(self) -> None:
        """Test that persistence errors don't show stack traces."""
        mock_service = MagicMock()
        mock_service.register.side_effect = PersistenceError()
        
        result = self.runner.invoke(
            cli,
            ["create", "--user", "1", "--category", "1", "--description", "test"],
            obj=CliContext(mock_service),
        )
        self.assertEqual(result.exit_code, 3)
        self.assertNotIn("Traceback", result.output)

    # ========== Empty List Tests ==========

    def test_list_with_no_results_shows_message(self) -> None:
        """Test that list command shows 'Нет заявок.' for empty results."""
        result = self.runner.invoke(
            cli,
            ["list", "--user", "99999"],
            obj=CliContext(self.service),
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Нет заявок", result.output)

    # ========== Integration Tests ==========

    def test_cannot_update_request_not_in_new_status(self) -> None:
        """Test that requests not in 'Новая' status cannot be updated."""
        # Create a request
        result = self.service.register(
            CreateRequestCommand(
                applicant_user_id=self.user.user_id,
                category_id=self.category.category_id,
                description="Test request",
            )
        )
        request_id = result.request.request_id
        
        # Try to update it (should succeed in "Новая" status)
        updated = self.service.update_request_description(request_id, "Updated")
        self.assertEqual(updated.description, "Updated")
        
        # Now change status to "В обработке"
        with self.database.unit_of_work() as uow:
            actor = uow.users.add(User(None, "actor", "Actor"))
        
        self.service.change_status(
            request_id,
            "В обработке",
            actor_user_id=actor.user_id,
            explanation="Processing",
        )
        
        # Try to update again - should fail
        with self.assertRaises(CannotUpdateRequestError):
            self.service.update_request_description(request_id, "Should fail")

    def test_full_flow_create_and_list(self) -> None:
        """Test full flow: create request and list it."""
        # Create a request
        result = self.service.register(
            CreateRequestCommand(
                applicant_user_id=self.user.user_id,
                category_id=self.category.category_id,
                description="Test request for listing",
            )
        )
        
        # List all requests
        list_result = self.service.list_requests()
        self.assertGreater(len(list_result.requests), 0)
        
        # Test via CLI
        cli_result = self.runner.invoke(cli, ["list"], obj=CliContext(self.service))
        self.assertEqual(cli_result.exit_code, 0)
        self.assertIn("ID", cli_result.output)
        self.assertIn("Пользователь", cli_result.output)
        self.assertNotIn("Нет заявок", cli_result.output)
