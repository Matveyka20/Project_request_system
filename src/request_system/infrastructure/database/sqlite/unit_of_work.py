"""SQLite unit of work that shares one transaction across repositories."""

from types import TracebackType

import sqlite3

from request_system.application.ports.persistence import (
    CrudRepository,
    PersistenceError,
    RequestRepository,
    StatusRepository,
)
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
from request_system.infrastructure.database.sqlite.repositories import (
    SQLiteRepository,
    SQLiteRequestRepository,
    SQLiteStatusRepository,
)


class SQLiteUnitOfWork:
    """One transaction and a typed repository for each schema table."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self.users: CrudRepository[User, int] = SQLiteRepository(
            connection, User, "Users", ("user_id",), "user_id"
        )
        self.roles: CrudRepository[Role, int] = SQLiteRepository(
            connection, Role, "Roles", ("role_id",), "role_id"
        )
        self.statuses: StatusRepository = SQLiteStatusRepository(connection)
        self.categories: CrudRepository[Category, int] = SQLiteRepository(
            connection, Category, "Categories", ("category_id",), "category_id"
        )
        self.user_roles: CrudRepository[UserRole, tuple[int, int]] = SQLiteRepository(
            connection, UserRole, "UserRoles", ("user_id", "role_id")
        )
        self.comments: CrudRepository[Comment, int] = SQLiteRepository(
            connection, Comment, "Comments", ("comment_id",), "comment_id"
        )
        history_repository: SQLiteRepository[RequestHistory, int] = SQLiteRepository(
            connection, RequestHistory, "RequestHistory", ("history_id",), "history_id"
        )
        self.request_history: CrudRepository[RequestHistory, int] = history_repository
        self.assignments: CrudRepository[Assignment, int] = SQLiteRepository(
            connection, Assignment, "Assignments", ("assignment_id",), "assignment_id"
        )
        self.attachments: CrudRepository[Attachment, int] = SQLiteRepository(
            connection, Attachment, "Attachments", ("attachment_id",), "attachment_id"
        )
        self.result_submissions: CrudRepository[ResultSubmission, int] = SQLiteRepository(
            connection,
            ResultSubmission,
            "ResultSubmissions",
            ("result_submission_id",),
            "result_submission_id",
        )
        self.acceptance_decisions: CrudRepository[AcceptanceDecision, int] = SQLiteRepository(
            connection,
            AcceptanceDecision,
            "AcceptanceDecisions",
            ("decision_id",),
            "decision_id",
        )
        self.requests: RequestRepository = SQLiteRequestRepository(
            connection,
            history_repository,
        )

    def __enter__(self) -> "SQLiteUnitOfWork":
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        try:
            if exception_type is None:
                self._connection.commit()
            else:
                self._connection.rollback()
        except sqlite3.Error as error:
            raise PersistenceError() from error
        finally:
            try:
                self._connection.close()
            except sqlite3.Error as error:
                raise PersistenceError() from error
        return False
