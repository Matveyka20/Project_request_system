"""Database lifecycle and SQLite unit-of-work factory."""

from pathlib import Path
import sqlite3

from request_system.application.ports.persistence import PersistenceError
from request_system.infrastructure.database.sqlite.unit_of_work import SQLiteUnitOfWork


class SQLiteDatabase:
    def __init__(self, database_path: str | Path, schema_path: str | Path) -> None:
        self._database_path = str(database_path)
        self._schema_path = Path(schema_path)

    def initialize(self) -> None:
        schema = self._schema_path.read_text(encoding="utf-8")
        connection: sqlite3.Connection | None = None
        try:
            connection = sqlite3.connect(self._database_path)
            connection.execute("PRAGMA foreign_keys = ON")
            connection.executescript(schema)
            connection.commit()
        except sqlite3.Error as error:
            raise PersistenceError() from error
        finally:
            if connection is not None:
                try:
                    connection.close()
                except sqlite3.Error as error:
                    raise PersistenceError() from error

    def unit_of_work(self) -> SQLiteUnitOfWork:
        connection: sqlite3.Connection | None = None
        try:
            connection = sqlite3.connect(self._database_path)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("BEGIN")
            return SQLiteUnitOfWork(connection)
        except sqlite3.Error as error:
            if connection is not None:
                try:
                    connection.close()
                except sqlite3.Error as close_error:
                    raise PersistenceError() from close_error
            raise PersistenceError() from error
