"""Persistence contracts; implementations belong to infrastructure adapters."""

from collections.abc import Sequence
from datetime import datetime
from types import TracebackType
from typing import Generic, Protocol, TypeVar

from request_system.domain.entities import (
    AcceptanceDecision,
    Assignment,
    Attachment,
    Category,
    Comment,
    Request,
    RequestHistory,
    ResultSubmission,
    Role,
    Status,
    User,
    UserRole,
)

EntityT = TypeVar("EntityT")
KeyT = TypeVar("KeyT")


class PersistenceError(RuntimeError):
    """Storage failure surfaced by a persistence adapter."""

    def __init__(self) -> None:
        super().__init__("Ошибка при работе с хранилищем данных.")


class CrudRepository(Protocol, Generic[EntityT, KeyT]):
    """CRUD operations for one entity type."""

    def add(self, entity: EntityT) -> EntityT: ...

    def get(self, key: KeyT) -> EntityT | None: ...

    def list_all(self) -> Sequence[EntityT]: ...

    def update(self, entity: EntityT) -> bool: ...

    def delete(self, key: KeyT) -> bool: ...


class RequestRepository(CrudRepository[Request, int], Protocol):
    """Request persistence with atomic creation of its first status event."""

    def create_with_initial_status(
        self,
        request: Request,
        *,
        actor_user_id: int,
        previous_status_id: int | None,
        new_status_id: int,
        occurred_at: datetime,
        explanation: str | None = None,
    ) -> tuple[Request, RequestHistory]: ...


class StatusRepository(CrudRepository[Status, int], Protocol):
    """Status lookup required by application workflows."""

    def get_by_name(self, name: str) -> Status | None: ...


class UnitOfWork(Protocol):
    """Repositories sharing one transaction."""

    users: CrudRepository[User, int]
    roles: CrudRepository[Role, int]
    statuses: StatusRepository
    categories: CrudRepository[Category, int]
    requests: RequestRepository
    user_roles: CrudRepository[UserRole, tuple[int, int]]
    comments: CrudRepository[Comment, int]
    request_history: CrudRepository[RequestHistory, int]
    assignments: CrudRepository[Assignment, int]
    attachments: CrudRepository[Attachment, int]
    result_submissions: CrudRepository[ResultSubmission, int]
    acceptance_decisions: CrudRepository[AcceptanceDecision, int]

    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None: ...
