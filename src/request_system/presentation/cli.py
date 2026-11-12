"""Command-line input and output for request registration."""

from collections.abc import Callable
import re

from request_system.application.ports.persistence import PersistenceError
from request_system.application.services.request_service import (
    CreateRequestCommand,
    InitialStatusNotConfigured,
    RequestService,
    RequestValidationError,
)


class CliInputError(ValueError):
    """Raised when a console value cannot be parsed."""


def _parse_identifier(value: str, field_name: str) -> int:
    stripped = value.strip()
    if not re.fullmatch(r"[+-]?[0-9]+", stripped):
        raise CliInputError(
            f"Введите целое число для поля «{field_name}»."
        )
    try:
        return int(stripped)
    except ValueError as error:
        raise CliInputError(
            f"Введите целое число для поля «{field_name}»."
        ) from error


def run_registration_cli(
    service: RequestService,
    *,
    input_fn: Callable[[str], str] | None = None,
    output_fn: Callable[[str], None] | None = None,
) -> int:
    read = input if input_fn is None else input_fn
    write = print if output_fn is None else output_fn
    write("Регистрация заявки")
    try:
        applicant_user_id = _parse_identifier(read("ID заявителя: "), "ID заявителя")
        category_id = _parse_identifier(read("ID категории: "), "ID категории")
        description = read("Описание заявки: ")
    except CliInputError as error:
        write(f"Ошибка ввода: {error}")
        return 2
    except EOFError:
        write("Ввод завершён. Заявка не создана.")
        return 2
    except KeyboardInterrupt:
        write("Регистрация отменена.")
        return 130

    try:
        result = service.register(
            CreateRequestCommand(
                applicant_user_id=applicant_user_id,
                description=description,
                category_id=category_id,
            )
        )
    except RequestValidationError as error:
        for message in error.errors.values():
            write(f"Ошибка: {message}")
        return 2
    except InitialStatusNotConfigured as error:
        write(f"Ошибка настройки системы: {error}")
        return 2
    except PersistenceError as error:
        write(f"Ошибка сохранения: {error}")
        return 3

    write("Заявка зарегистрирована.")
    write(f"Номер: {result.request.request_number}")
    write(f"ID: {result.request.request_id}")
    write(f"Дата регистрации: {result.request.registered_at.isoformat()}")
    write(f"Статус: {result.initial_status.name}")
    return 0
