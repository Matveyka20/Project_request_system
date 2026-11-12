"""Command-line entry point for the request system."""

import os
from pathlib import Path
import sys

from request_system.application.ports.persistence import PersistenceError
from request_system.application.services.request_service import RequestService
from request_system.infrastructure.database.sqlite import SQLiteDatabase
from request_system.presentation.cli import run_registration_cli


def main() -> int:
    repository_root = Path(__file__).resolve().parents[2]
    database_path = Path(
        os.environ.get(
            "REQUEST_SYSTEM_DB",
            str(repository_root / "request-system.db"),
        )
    )
    database = SQLiteDatabase(
        database_path,
        repository_root / "docs" / "sql" / "schema.sql",
    )
    try:
        database.initialize()
    except PersistenceError as error:
        print(f"Ошибка запуска хранилища: {error}", file=sys.stderr)
        return 3

    return run_registration_cli(RequestService(database.unit_of_work))


if __name__ == "__main__":
    raise SystemExit(main())
