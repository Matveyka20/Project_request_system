"""Business rules for registering a new request."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from request_system.application.ports.persistence import UnitOfWork
from request_system.domain.entities import Request, Status

INITIAL_STATUS_NAME = "Новая"


@dataclass(frozen=True, slots=True)
class CreateRequestCommand:
    applicant_user_id: int
    description: str
    category_id: int


@dataclass(frozen=True, slots=True)
class RequestRegistrationResult:
    request: Request
    initial_status: Status


class RequestValidationError(ValueError):
    def __init__(self, errors: dict[str, str]) -> None:
        self.errors = errors.copy()
        super().__init__("; ".join(errors.values()))


class InitialStatusNotConfigured(RuntimeError):
    def __init__(self) -> None:
        super().__init__(f"Начальный статус «{INITIAL_STATUS_NAME}» не настроен.")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _new_request_number() -> str:
    return f"REQ-{uuid4().hex.upper()}"


class RequestService:
    """Validate registration input and coordinate request persistence."""

    def __init__(
        self,
        unit_of_work_factory: Callable[[], UnitOfWork],
        *,
        clock: Callable[[], datetime] = _utc_now,
        request_number_factory: Callable[[], str] = _new_request_number,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        self._request_number_factory = request_number_factory

    def register(self, command: CreateRequestCommand) -> RequestRegistrationResult:
        errors: dict[str, str] = {}
        description = command.description.strip()
        if not description:
            errors["description"] = "Укажите описание заявки."
        if command.applicant_user_id <= 0:
            errors["applicant_user_id"] = "Укажите корректного заявителя."
        if command.category_id <= 0:
            errors["category_id"] = "Укажите корректную категорию."
        if errors:
            raise RequestValidationError(errors)

        with self._unit_of_work_factory() as unit_of_work:
            if unit_of_work.users.get(command.applicant_user_id) is None:
                errors["applicant_user_id"] = "Заявитель не найден."
            if unit_of_work.categories.get(command.category_id) is None:
                errors["category_id"] = "Категория не найдена."
            if errors:
                raise RequestValidationError(errors)

            initial_status = unit_of_work.statuses.get_by_name(INITIAL_STATUS_NAME)
            if initial_status is None or initial_status.status_id is None:
                raise InitialStatusNotConfigured()

            registered_at = self._clock()
            if registered_at.tzinfo is None or registered_at.utcoffset() is None:
                raise RuntimeError("Часы приложения должны возвращать время с часовым поясом.")

            request_number = self._request_number_factory()
            if not request_number.strip():
                raise RuntimeError("Генератор номера заявки вернул пустое значение.")

            request, _ = unit_of_work.requests.create_with_initial_status(
                Request(
                    request_id=None,
                    request_number=request_number,
                    description=description,
                    applicant_user_id=command.applicant_user_id,
                    category_id=command.category_id,
                    priority=None,
                    registered_at=registered_at,
                ),
                actor_user_id=command.applicant_user_id,
                previous_status_id=None,
                new_status_id=initial_status.status_id,
                occurred_at=registered_at,
            )
            if request.request_id is None:
                raise RuntimeError("Репозиторий не назначил заявке идентификатор.")
            return RequestRegistrationResult(request, initial_status)
