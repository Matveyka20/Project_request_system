"""SQLite implementations of the application's persistence ports."""

from dataclasses import asdict, fields, replace
from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar

import sqlite3

from request_system.application.ports.persistence import (
    PersistenceError,
    RequestRepository,
    StatusRepository,
)
from request_system.domain.entities import (
    AcceptanceDecision,
    AcceptanceOutcome,
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
SQLiteValue = None | int | float | str | bytes

_DATETIME_FIELDS = {
    "registered_at",
    "created_at",
    "occurred_at",
    "assigned_at",
    "ended_at",
    "submitted_at",
    "decided_at",
}


def _execute(
    connection: sqlite3.Connection,
    statement: str,
    parameters: tuple[object, ...] = (),
) -> sqlite3.Cursor:
    try:
        return connection.execute(statement, parameters)
    except sqlite3.Error as error:
        raise PersistenceError() from error


def _encode(value: object) -> SQLiteValue:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        if isinstance(value.value, (int, float, str, bytes)):
            return value.value
        raise TypeError(f"Unsupported enum value for SQLite: {value.value!r}")
    if isinstance(value, bool):
        return int(value)
    if value is None or isinstance(value, (int, float, str, bytes)):
        return value
    raise TypeError(f"Unsupported value for SQLite: {type(value).__name__}")


class SQLiteRepository(Generic[EntityT, KeyT]):
    """Generic CRUD adapter for one schema table."""

    def __init__(
        self,
        connection: sqlite3.Connection,
        entity_type: type[EntityT],
        table: str,
        key_columns: tuple[str, ...],
        generated_key_column: str | None = None,
    ) -> None:
        self._connection = connection
        self._entity_type = entity_type
        self._table = table
        self._key_columns = key_columns
        self._generated_key_column = generated_key_column
        self._columns = tuple(field.name for field in fields(entity_type))

    def add(self, entity: EntityT) -> EntityT:
        values = {name: _encode(value) for name, value in asdict(entity).items()}
        if self._generated_key_column and values[self._generated_key_column] is None:
            values.pop(self._generated_key_column)

        columns = tuple(values)
        placeholders = ", ".join("?" for _ in columns)
        column_sql = ", ".join(columns)
        cursor = _execute(
            self._connection,
            f"INSERT INTO {self._table} ({column_sql}) VALUES ({placeholders})",
            tuple(values[column] for column in columns),
        )

        if self._generated_key_column and getattr(entity, self._generated_key_column) is None:
            return replace(entity, **{self._generated_key_column: cursor.lastrowid})
        return entity

    def get(self, key: KeyT) -> EntityT | None:
        key_values = self._key_values(key)
        where = " AND ".join(f"{column} = ?" for column in self._key_columns)
        row = _execute(
            self._connection,
            f"SELECT * FROM {self._table} WHERE {where}",
            key_values,
        ).fetchone()
        return self._from_row(row) if row is not None else None

    def list_all(self) -> list[EntityT]:
        order_by = ", ".join(self._key_columns)
        rows = _execute(
            self._connection,
            f"SELECT * FROM {self._table} ORDER BY {order_by}"
        ).fetchall()
        return [self._from_row(row) for row in rows]

    def update(self, entity: EntityT) -> bool:
        values = {name: _encode(value) for name, value in asdict(entity).items()}
        key_values = tuple(values[column] for column in self._key_columns)
        if any(value is None for value in key_values):
            raise ValueError(f"{self._table} entity must have a complete key before update")

        update_columns = tuple(column for column in self._columns if column not in self._key_columns)
        if not update_columns:
            where = " AND ".join(f"{column} = ?" for column in self._key_columns)
            row = _execute(
                self._connection,
                f"SELECT 1 FROM {self._table} WHERE {where}",
                key_values,
            ).fetchone()
            return row is not None
        assignments = ", ".join(f"{column} = ?" for column in update_columns)
        where = " AND ".join(f"{column} = ?" for column in self._key_columns)
        cursor = _execute(
            self._connection,
            f"UPDATE {self._table} SET {assignments} WHERE {where}",
            tuple(values[column] for column in update_columns) + key_values,
        )
        return cursor.rowcount > 0

    def delete(self, key: KeyT) -> bool:
        key_values = self._key_values(key)
        where = " AND ".join(f"{column} = ?" for column in self._key_columns)
        cursor = _execute(
            self._connection,
            f"DELETE FROM {self._table} WHERE {where}",
            key_values,
        )
        return cursor.rowcount > 0

    def _key_values(self, key: KeyT) -> tuple[int, ...]:
        if len(self._key_columns) == 1:
            if isinstance(key, tuple) or not isinstance(key, int):
                raise ValueError(f"{self._table} requires a single-column key")
            return (key,)
        if (
            not isinstance(key, tuple)
            or len(key) != len(self._key_columns)
            or any(not isinstance(value, int) for value in key)
        ):
            raise ValueError(f"{self._table} requires a {len(self._key_columns)}-column key")
        return key

    def _from_row(self, row: sqlite3.Row) -> EntityT:
        values: dict[str, Any] = dict(row)
        for name in _DATETIME_FIELDS:
            if name in values and values[name] is not None:
                values[name] = datetime.fromisoformat(values[name])
        if "is_service" in values:
            values["is_service"] = bool(values["is_service"])
        if self._entity_type is AcceptanceDecision:
            values["outcome"] = AcceptanceOutcome(values["outcome"])
        return self._entity_type(**values)


class SQLiteRequestRepository(
    SQLiteRepository[Request, int],
    RequestRepository,
):
    def __init__(
        self,
        connection: sqlite3.Connection,
        history: SQLiteRepository[RequestHistory, int],
    ) -> None:
        super().__init__(connection, Request, "Requests", ("request_id",), "request_id")
        self._history = history

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
        _execute(self._connection, "SAVEPOINT create_request_with_initial_status")
        try:
            saved_request = self.add(request)
            if saved_request.request_id is None:
                raise RuntimeError("SQLite did not assign a request ID")
            initial_history = self._history.add(
                RequestHistory(
                    history_id=None,
                    request_id=saved_request.request_id,
                    actor_user_id=actor_user_id,
                    previous_status_id=previous_status_id,
                    new_status_id=new_status_id,
                    occurred_at=occurred_at,
                    explanation=explanation,
                )
            )
        except BaseException:
            _execute(
                self._connection,
                "ROLLBACK TO SAVEPOINT create_request_with_initial_status"
            )
            _execute(
                self._connection,
                "RELEASE SAVEPOINT create_request_with_initial_status"
            )
            raise
        _execute(self._connection, "RELEASE SAVEPOINT create_request_with_initial_status")
        return saved_request, initial_history


class SQLiteStatusRepository(SQLiteRepository[Status, int], StatusRepository):
    def __init__(self, connection: sqlite3.Connection) -> None:
        super().__init__(connection, Status, "Statuses", ("status_id",), "status_id")

    def get_by_name(self, name: str) -> Status | None:
        row = _execute(
            self._connection,
            "SELECT * FROM Statuses WHERE name = ?",
            (name,),
        ).fetchone()
        return self._from_row(row) if row is not None else None
