import ast
from datetime import datetime, timezone
from pathlib import Path
import unittest

from request_system.application.services.request_service import (
    CreateRequestCommand,
    InitialStatusNotConfigured,
    RequestService,
    RequestValidationError,
)
from request_system.domain.entities import (
    Category,
    Request,
    RequestHistory,
    Status,
    User,
)


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 11, 12, 12, 0, tzinfo=timezone.utc)


class LookupRepository:
    def __init__(self, entities: dict[int, object]) -> None:
        self._entities = entities

    def get(self, key: int) -> object | None:
        return self._entities.get(key)


class FakeStatusRepository:
    def __init__(self, status: Status | None) -> None:
        self.status = status
        self.looked_up_name: str | None = None

    def get_by_name(self, name: str) -> Status | None:
        self.looked_up_name = name
        return self.status


class FakeRequestRepository:
    def __init__(self) -> None:
        self.calls: list[tuple[Request, int, int, datetime]] = []
        self.created_history: RequestHistory | None = None

    def create_with_initial_status(
        self,
        request: Request,
        *,
        actor_user_id: int,
        previous_status_id: int | None,
        new_status_id: int,
        occurred_at: datetime,
        explanation: str | None = None,
    ) -> tuple[Request, RequestHistory]:
        self.calls.append(
            (request, actor_user_id, previous_status_id, new_status_id, occurred_at)
        )
        saved_request = Request(
            request_id=41,
            request_number=request.request_number,
            description=request.description,
            applicant_user_id=request.applicant_user_id,
            category_id=request.category_id,
            priority=request.priority,
            registered_at=request.registered_at,
        )
        self.created_history = RequestHistory(
            history_id=51,
            request_id=41,
            actor_user_id=actor_user_id,
            previous_status_id=previous_status_id,
            new_status_id=new_status_id,
            occurred_at=occurred_at,
            explanation=explanation,
        )
        return saved_request, self.created_history


class FakeUnitOfWork:
    def __init__(self, status: Status | None) -> None:
        self.users = LookupRepository({7: User(7, "applicant", "Applicant")})
        self.categories = LookupRepository({8: Category(8, "repair")})
        self.statuses = FakeStatusRepository(status)
        self.requests = FakeRequestRepository()
        self.exit_exception: type[BaseException] | None = None

    def __enter__(self) -> "FakeUnitOfWork":
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: object,
    ) -> bool:
        self.exit_exception = exception_type
        return False


class RequestServiceTests(unittest.TestCase):
    def create_service(
        self,
        status: Status | None = Status(3, "Новая"),
    ) -> tuple[RequestService, FakeUnitOfWork, list[int]]:
        unit_of_work = FakeUnitOfWork(status)
        factory_calls = [0]

        def unit_of_work_factory() -> FakeUnitOfWork:
            factory_calls[0] += 1
            return unit_of_work

        service = RequestService(
            unit_of_work_factory,
            clock=lambda: NOW,
            request_number_factory=lambda: "REQ-TEST-1",
        )
        return service, unit_of_work, factory_calls

    def test_register_valid_request_through_ports(self) -> None:
        service, unit_of_work, factory_calls = self.create_service()

        result = service.register(CreateRequestCommand(7, "  Projector repair  ", 8))

        self.assertEqual(factory_calls[0], 1)
        self.assertEqual(result.request.request_id, 41)
        self.assertEqual(result.request.request_number, "REQ-TEST-1")
        self.assertEqual(result.request.description, "Projector repair")
        self.assertEqual(result.request.applicant_user_id, 7)
        self.assertEqual(result.request.category_id, 8)
        self.assertEqual(result.request.priority, None)
        self.assertEqual(result.request.registered_at, NOW)
        self.assertEqual(result.initial_status, Status(3, "Новая"))
        self.assertEqual(unit_of_work.statuses.looked_up_name, "Новая")
        self.assertEqual(
            unit_of_work.requests.calls,
            [
                (
                    Request(None, "REQ-TEST-1", "Projector repair", 7, 8, None, NOW),
                    7,
                    None,
                    3,
                    NOW,
                )
            ],
        )
        self.assertIsNotNone(unit_of_work.requests.created_history)
        self.assertEqual(unit_of_work.requests.created_history.previous_status_id, None)
        self.assertEqual(unit_of_work.requests.created_history.new_status_id, 3)
        self.assertIsNone(unit_of_work.exit_exception)

    def test_invalid_input_is_rejected_before_opening_unit_of_work(self) -> None:
        service, unit_of_work, factory_calls = self.create_service()

        with self.assertRaises(RequestValidationError) as raised:
            service.register(CreateRequestCommand(0, "   ", -1))

        self.assertEqual(
            set(raised.exception.errors),
            {"description", "applicant_user_id", "category_id"},
        )
        self.assertEqual(factory_calls[0], 0)
        self.assertEqual(unit_of_work.requests.calls, [])

    def test_unknown_applicant_and_category_are_rejected_without_writes(self) -> None:
        service, unit_of_work, _ = self.create_service()

        with self.assertRaises(RequestValidationError) as raised:
            service.register(CreateRequestCommand(99, "Valid description", 98))

        self.assertEqual(set(raised.exception.errors), {"applicant_user_id", "category_id"})
        self.assertEqual(unit_of_work.requests.calls, [])
        self.assertIs(raised.exception.__class__, unit_of_work.exit_exception)

    def test_missing_initial_status_fails_without_writing(self) -> None:
        service, unit_of_work, _ = self.create_service(status=None)

        with self.assertRaises(InitialStatusNotConfigured):
            service.register(CreateRequestCommand(7, "Valid description", 8))

        self.assertEqual(unit_of_work.requests.calls, [])
        self.assertIs(InitialStatusNotConfigured, unit_of_work.exit_exception)

    def test_service_has_no_sqlite_or_presentation_dependency(self) -> None:
        service_path = (
            ROOT
            / "src"
            / "request_system"
            / "application"
            / "services"
            / "request_service.py"
        )
        tree = ast.parse(service_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules = [node.module]
            else:
                continue
            for module in imported_modules:
                self.assertNotIn(
                    module.split(".")[0],
                    {"sqlite3", "presentation"},
                    module,
                )
                self.assertNotIn("infrastructure", module.split("."), module)


if __name__ == "__main__":
    unittest.main()
