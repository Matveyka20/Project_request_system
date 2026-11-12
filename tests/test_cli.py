from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import os
from pathlib import Path
import tempfile
from unittest import TestCase
from unittest.mock import patch

from request_system.__main__ import main
from request_system.application.ports.persistence import PersistenceError
from request_system.application.services.request_service import (
    InitialStatusNotConfigured,
    RequestRegistrationResult,
    RequestValidationError,
)
from request_system.domain.entities import Category, Status, User
from request_system.infrastructure.database.sqlite import SQLiteDatabase
from request_system.presentation.cli import run_registration_cli

ROOT = Path(__file__).resolve().parents[1]


class StubRequestService:
    def __init__(self, outcome: object = None) -> None:
        self.outcome = outcome
        self.calls = 0

    def register(self, command: object) -> RequestRegistrationResult:
        self.calls += 1
        if isinstance(self.outcome, BaseException):
            raise self.outcome
        if self.outcome is not None:
            return self.outcome
        raise AssertionError("Unexpected call to the request service")


class CliTests(TestCase):
    def run_cli(
        self,
        values: list[str],
        service: StubRequestService,
    ) -> tuple[int, list[str]]:
        remaining = iter(values)
        messages: list[str] = []

        def input_fn(_prompt: str) -> str:
            try:
                return next(remaining)
            except StopIteration as error:
                raise EOFError from error

        exit_code = run_registration_cli(
            service,
            input_fn=input_fn,
            output_fn=messages.append,
        )
        return exit_code, messages

    def test_non_numeric_applicant_id_is_reported_without_service_call(self) -> None:
        service = StubRequestService()

        exit_code, messages = self.run_cli(["not-an-id"], service)

        self.assertEqual(exit_code, 2)
        self.assertEqual(service.calls, 0)
        self.assertIn("Введите целое число для поля «ID заявителя».", messages[-1])

    def test_unparseably_large_numeric_id_is_reported_without_service_call(self) -> None:
        service = StubRequestService()

        exit_code, messages = self.run_cli(["9" * 5000], service)

        self.assertEqual(exit_code, 2)
        self.assertEqual(service.calls, 0)
        self.assertIn("Введите целое число для поля «ID заявителя».", messages[-1])

    def test_empty_category_id_is_reported_without_service_call(self) -> None:
        service = StubRequestService()

        exit_code, messages = self.run_cli(["1", "  "], service)

        self.assertEqual(exit_code, 2)
        self.assertEqual(service.calls, 0)
        self.assertIn("Введите целое число для поля «ID категории».", messages[-1])

    def test_business_validation_error_is_shown_without_traceback(self) -> None:
        service = StubRequestService(
            RequestValidationError({"description": "Укажите описание заявки."})
        )

        exit_code, messages = self.run_cli(["1", "2", "   "], service)

        self.assertEqual(exit_code, 2)
        self.assertEqual(service.calls, 1)
        self.assertEqual(messages[-1], "Ошибка: Укажите описание заявки.")

    def test_missing_initial_status_is_reported(self) -> None:
        service = StubRequestService(InitialStatusNotConfigured())

        exit_code, messages = self.run_cli(["1", "2", "Description"], service)

        self.assertEqual(exit_code, 2)
        self.assertIn("Ошибка настройки системы:", messages[-1])
        self.assertNotIn("Traceback", "\n".join(messages))

    def test_persistence_error_is_reported_with_failure_exit_code(self) -> None:
        service = StubRequestService(PersistenceError())

        exit_code, messages = self.run_cli(["1", "2", "Description"], service)

        self.assertEqual(exit_code, 3)
        self.assertEqual(messages[-1], "Ошибка сохранения: Ошибка при работе с хранилищем данных.")
        self.assertNotIn("Заявка зарегистрирована.", messages)

    def test_unexpected_error_is_not_swallowed_or_reported_as_success(self) -> None:
        service = StubRequestService(RuntimeError("unexpected failure"))
        messages: list[str] = []
        input_values = iter(("1", "2", "Description"))

        with self.assertRaisesRegex(RuntimeError, "unexpected failure"):
            run_registration_cli(
                service,
                input_fn=lambda _prompt: next(input_values),
                output_fn=messages.append,
            )

        self.assertNotIn("Заявка зарегистрирована.", messages)

    def test_eof_during_input_is_a_clean_user_error(self) -> None:
        service = StubRequestService()

        exit_code, messages = self.run_cli([], service)

        self.assertEqual(exit_code, 2)
        self.assertEqual(service.calls, 0)
        self.assertEqual(messages[-1], "Ввод завершён. Заявка не создана.")

    def test_startup_storage_error_is_reported_without_traceback(self) -> None:
        with patch("request_system.__main__.SQLiteDatabase") as database_type:
            database_type.return_value.initialize.side_effect = PersistenceError()
            stderr = StringIO()
            with redirect_stderr(stderr):
                exit_code = main()

        self.assertEqual(exit_code, 3)
        self.assertIn("Ошибка запуска хранилища:", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_unexpected_startup_error_is_not_swallowed(self) -> None:
        with patch("request_system.__main__.SQLiteDatabase") as database_type:
            database_type.return_value.initialize.side_effect = RuntimeError("startup failure")
            with redirect_stdout(StringIO()):
                with self.assertRaisesRegex(RuntimeError, "startup failure"):
                    main()

    def test_main_registers_request_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "cli.sqlite3"
            database = SQLiteDatabase(
                database_path,
                ROOT / "docs" / "sql" / "schema.sql",
            )
            database.initialize()
            with database.unit_of_work() as unit_of_work:
                applicant = unit_of_work.users.add(User(None, "cli-applicant", "CLI Applicant"))
                category = unit_of_work.categories.add(Category(None, "repair"))
                unit_of_work.statuses.add(Status(None, "Новая"))

            output = StringIO()
            with patch.dict(os.environ, {"REQUEST_SYSTEM_DB": str(database_path)}):
                with patch(
                    "builtins.input",
                    side_effect=[
                        str(applicant.user_id),
                        str(category.category_id),
                        "  Repair projector  ",
                    ],
                ):
                    with redirect_stdout(output):
                        exit_code = main()

            self.assertEqual(exit_code, 0)
            self.assertIn("Заявка зарегистрирована.", output.getvalue())
            self.assertIn("Статус: Новая", output.getvalue())
            with database.unit_of_work() as unit_of_work:
                requests = unit_of_work.requests.list_all()
                self.assertEqual(len(requests), 1)
                self.assertEqual(requests[0].description, "Repair projector")
