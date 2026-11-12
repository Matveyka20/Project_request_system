"""Business rules for registering a new request."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from uuid import uuid4

from request_system.application.ports.persistence import UnitOfWork
from request_system.domain.entities import Request, RequestHistory, Status

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


@dataclass(frozen=True, slots=True)
class GetRequestResult:
    request: Request
    status: Status
    user_name: str
    category_name: str


@dataclass(frozen=True, slots=True)
class ListRequestsResult:
    requests: Sequence[tuple[Request, Status, str, str]]  # (request, status, user_name, category_name)


class RequestValidationError(ValueError):
    def __init__(self, errors: dict[str, str]) -> None:
        self.errors = errors.copy()
        super().__init__("; ".join(errors.values()))


class InitialStatusNotConfigured(RuntimeError):
    def __init__(self) -> None:
        super().__init__(f"Начальный статус «{INITIAL_STATUS_NAME}» не настроен.")


class RequestNotFoundError(ValueError):
    """Raised when a request with the given ID does not exist."""

    def __init__(self, request_id: int) -> None:
        self.request_id = request_id
        super().__init__(f"Заявка с ID {request_id} не найдена.")


class CannotUpdateRequestError(ValueError):
    """Raised when a request cannot be updated due to its current status."""

    def __init__(self, request_id: int, current_status: str) -> None:
        self.request_id = request_id
        self.current_status = current_status
        super().__init__(
            f"Нельзя редактировать заявку в статусе «{current_status}»."
        )


class InvalidStatusTransitionError(ValueError):
    """Raised when a status transition is not allowed."""

    def __init__(self, current_status: str, requested_status: str) -> None:
        self.current_status = current_status
        self.requested_status = requested_status
        super().__init__(
            f"Невозможно перейти из статуса «{current_status}» в «{requested_status}»."
        )


class StatusNotFoundError(ValueError):
    """Raised when a status with the given name does not exist."""

    def __init__(self, status_name: str) -> None:
        self.status_name = status_name
        super().__init__(f"Статус «{status_name}» не найден в системе.")


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

    def get_request(self, request_id: int) -> GetRequestResult:
        """Retrieve a request by ID with related entities."""
        with self._unit_of_work_factory() as unit_of_work:
            request = unit_of_work.requests.get(request_id)
            if request is None:
                raise RequestNotFoundError(request_id)

            user = unit_of_work.users.get(request.applicant_user_id)
            if user is None:
                raise RuntimeError(f"User {request.applicant_user_id} not found for request.")

            category = unit_of_work.categories.get(request.category_id) if request.category_id else None
            category_name = category.name if category else "Unknown"

            history = unit_of_work.request_history.list_all()
            latest_history = next(
                (h for h in reversed(history) if h.request_id == request_id),
                None,
            )
            if latest_history is None:
                raise RuntimeError(f"No history found for request {request_id}.")

            status = unit_of_work.statuses.get(latest_history.new_status_id)
            if status is None:
                raise RuntimeError(f"Status {latest_history.new_status_id} not found.")

            return GetRequestResult(
                request=request,
                status=status,
                user_name=user.name,
                category_name=category_name,
            )

    def update_request_description(
        self, request_id: int, new_description: str
    ) -> Request:
        """Update a request's description (only if status is 'New')."""
        new_description = new_description.strip()
        if not new_description:
            raise RequestValidationError(
                {"description": "Укажите описание заявки."}
            )

        with self._unit_of_work_factory() as unit_of_work:
            request = unit_of_work.requests.get(request_id)
            if request is None:
                raise RequestNotFoundError(request_id)

            history = unit_of_work.request_history.list_all()
            latest_history = next(
                (h for h in reversed(history) if h.request_id == request_id),
                None,
            )
            if latest_history is None:
                raise RuntimeError(f"No history found for request {request_id}.")

            status = unit_of_work.statuses.get(latest_history.new_status_id)
            if status is None:
                raise RuntimeError(f"Status {latest_history.new_status_id} not found.")

            if status.name != INITIAL_STATUS_NAME:
                raise CannotUpdateRequestError(request_id, status.name)

            updated_request = replace(request, description=new_description)
            unit_of_work.requests.update(updated_request)
            return updated_request

    def list_requests(
        self,
        *,
        user_id: int | None = None,
        category_id: int | None = None,
        status_name: str | None = None,
    ) -> ListRequestsResult:
        """List requests with optional filters."""
        with self._unit_of_work_factory() as unit_of_work:
            all_requests = unit_of_work.requests.list_all()
            all_history = unit_of_work.request_history.list_all()

            results: list[tuple[Request, Status, str, str]] = []

            for request in all_requests:
                if user_id is not None and request.applicant_user_id != user_id:
                    continue
                if category_id is not None and request.category_id != category_id:
                    continue

                latest_history = next(
                    (h for h in reversed(all_history) if h.request_id == request.request_id),
                    None,
                )
                if latest_history is None:
                    continue

                status = unit_of_work.statuses.get(latest_history.new_status_id)
                if status is None:
                    continue

                if status_name is not None and status.name != status_name:
                    continue

                user = unit_of_work.users.get(request.applicant_user_id)
                user_name = user.name if user else "Unknown"

                category = unit_of_work.categories.get(request.category_id) if request.category_id else None
                category_name = category.name if category else "Unknown"

                results.append((request, status, user_name, category_name))

            return ListRequestsResult(requests=results)

    def change_status(
        self,
        request_id: int,
        new_status_name: str,
        *,
        actor_user_id: int,
        explanation: str | None = None,
    ) -> tuple[Request, RequestHistory]:
        """Change request status with validation and history recording."""
        with self._unit_of_work_factory() as unit_of_work:
            request = unit_of_work.requests.get(request_id)
            if request is None:
                raise RequestNotFoundError(request_id)

            new_status = unit_of_work.statuses.get_by_name(new_status_name)
            if new_status is None or new_status.status_id is None:
                raise StatusNotFoundError(new_status_name)

            history = unit_of_work.request_history.list_all()
            latest_history = next(
                (h for h in reversed(history) if h.request_id == request_id),
                None,
            )
            if latest_history is None:
                raise RuntimeError(f"No history found for request {request_id}.")

            current_status = unit_of_work.statuses.get(latest_history.new_status_id)
            if current_status is None:
                raise RuntimeError(f"Status {latest_history.new_status_id} not found.")

            if current_status.name == new_status_name:
                raise RequestValidationError(
                    {"status": f"Заявка уже находится в статусе «{new_status_name}»."}
                )

            occurred_at = self._clock()
            if occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
                raise RuntimeError("Часы приложения должны возвращать время с часовым поясом.")

            _, history_record = unit_of_work.requests.create_with_initial_status(
                request,
                actor_user_id=actor_user_id,
                previous_status_id=current_status.status_id,
                new_status_id=new_status.status_id,
                occurred_at=occurred_at,
                explanation=explanation,
            )

            return request, history_record

