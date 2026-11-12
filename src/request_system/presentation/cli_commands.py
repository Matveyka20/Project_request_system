"""Command-line interface for the request system using Click."""

from typing import Optional

import click

from request_system.application.services.request_service import (
    CannotUpdateRequestError,
    CreateRequestCommand,
    InvalidStatusTransitionError,
    InitialStatusNotConfigured,
    RequestNotFoundError,
    RequestService,
    RequestValidationError,
    StatusNotFoundError,
)
from request_system.application.ports.persistence import PersistenceError


class CliContext:
    """Context for CLI commands."""

    def __init__(self, service: RequestService) -> None:
        self.service = service


def format_error_message(error: BaseException) -> str:
    """Format an error message for display to the user."""
    if isinstance(error, RequestValidationError):
        return "; ".join(error.errors.values())
    if isinstance(error, (
        RequestNotFoundError,
        CannotUpdateRequestError,
        InvalidStatusTransitionError,
        StatusNotFoundError,
        InitialStatusNotConfigured,
    )):
        return str(error)
    if isinstance(error, PersistenceError):
        return f"Ошибка сохранения: {error}"
    return str(error)


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Request system CLI."""
    pass


@cli.command()
@click.option("--user", "user_id", type=int, required=True, help="User ID")
@click.option("--category", "category_id", type=int, required=True, help="Category ID")
@click.option("--description", required=True, help="Request description")
@click.pass_obj
def create(ctx: CliContext, user_id: int, category_id: int, description: str) -> None:
    """Create a new request."""
    try:
        command = CreateRequestCommand(
            applicant_user_id=user_id,
            category_id=category_id,
            description=description,
        )
        result = ctx.service.register(command)
        click.echo(f"Заявка создана")
        click.echo(f"ID: {result.request.request_id}")
        click.echo(f"Номер: {result.request.request_number}")
        click.echo(f"Статус: {result.initial_status.name}")
        click.echo(f"Дата: {result.request.registered_at.isoformat()}")
    except (RequestValidationError, InitialStatusNotConfigured) as error:
        click.echo(f"Ошибка: {format_error_message(error)}", err=True)
        raise click.Exit(2)
    except PersistenceError as error:
        click.echo(f"Ошибка: {format_error_message(error)}", err=True)
        raise click.Exit(3)


@cli.command()
@click.argument("request_id", type=int)
@click.pass_obj
def get(ctx: CliContext, request_id: int) -> None:
    """Get a request by ID."""
    try:
        result = ctx.service.get_request(request_id)
        click.echo(f"ID: {result.request.request_id}")
        click.echo(f"Номер: {result.request.request_number}")
        click.echo(f"Заявитель: {result.user_name}")
        click.echo(f"Категория: {result.category_name}")
        click.echo(f"Описание: {result.request.description}")
        click.echo(f"Статус: {result.status.name}")
        click.echo(f"Создана: {result.request.registered_at.isoformat()}")
    except RequestNotFoundError as error:
        click.echo(f"Ошибка: {error}", err=True)
        raise click.Exit(2)
    except (PersistenceError, RuntimeError) as error:
        click.echo(f"Ошибка: {format_error_message(error)}", err=True)
        raise click.Exit(3)


@cli.command()
@click.argument("request_id", type=int)
@click.option("--description", required=True, help="New description")
@click.pass_obj
def update(ctx: CliContext, request_id: int, description: str) -> None:
    """Update a request's description."""
    try:
        updated = ctx.service.update_request_description(request_id, description)
        click.echo(f"Заявка обновлена")
        click.echo(f"ID: {updated.request_id}")
        click.echo(f"Новое описание: {updated.description}")
    except (RequestNotFoundError, CannotUpdateRequestError, RequestValidationError) as error:
        click.echo(f"Ошибка: {error}", err=True)
        raise click.Exit(2)
    except (PersistenceError, RuntimeError) as error:
        click.echo(f"Ошибка: {format_error_message(error)}", err=True)
        raise click.Exit(3)


@cli.command("list")
@click.option("--user", "user_id", type=Optional[int], help="Filter by user ID")
@click.option("--category", "category_id", type=Optional[int], help="Filter by category ID")
@click.option("--status", "status_name", type=Optional[str], help="Filter by status")
@click.pass_obj
def list_cmd(
    ctx: CliContext,
    user_id: Optional[int],
    category_id: Optional[int],
    status_name: Optional[str],
) -> None:
    """List requests with optional filters."""
    try:
        result = ctx.service.list_requests(
            user_id=user_id,
            category_id=category_id,
            status_name=status_name,
        )

        if not result.requests:
            click.echo("Нет заявок.")
            return

        # Print table header
        click.echo(f"{'ID':<6} | {'Пользователь':<20} | {'Категория':<15} | {'Статус':<12} | {'Создана':<26}")
        click.echo("-" * 90)

        # Print table rows
        for request, status, user_name, category_name in result.requests:
            click.echo(
                f"{request.request_id:<6} | {user_name:<20} | {category_name:<15} | "
                f"{status.name:<12} | {request.registered_at.isoformat():<26}"
            )
    except (PersistenceError, RuntimeError) as error:
        click.echo(f"Ошибка: {format_error_message(error)}", err=True)
        raise click.Exit(3)


@cli.command("status")
@click.argument("request_id", type=int)
@click.option("--new-status", "new_status_name", required=True, help="New status name")
@click.option("--reason", type=Optional[str], help="Reason for status change")
@click.option("--actor", "actor_user_id", type=int, required=True, help="Actor user ID")
@click.pass_obj
def status_cmd(
    ctx: CliContext,
    request_id: int,
    new_status_name: str,
    reason: Optional[str],
    actor_user_id: int,
) -> None:
    """Change request status."""
    try:
        current_result = ctx.service.get_request(request_id)
        current_status = current_result.status.name

        _, history = ctx.service.change_status(
            request_id,
            new_status_name,
            actor_user_id=actor_user_id,
            explanation=reason,
        )

        click.echo(f"Статус изменен")
        click.echo(f"Заявка ID: {request_id}")
        click.echo(f"Старый статус: {current_status}")
        click.echo(f"Новый статус: {new_status_name}")
    except (
        RequestNotFoundError,
        InvalidStatusTransitionError,
        StatusNotFoundError,
        RequestValidationError,
    ) as error:
        click.echo(f"Ошибка: {error}", err=True)
        raise click.Exit(2)
    except (PersistenceError, RuntimeError) as error:
        click.echo(f"Ошибка: {format_error_message(error)}", err=True)
        raise click.Exit(3)


def run_cli(service: RequestService) -> int:
    """Run the CLI with the given service."""
    try:
        cli(obj=CliContext(service), standalone_mode=True)
        return 0
    except SystemExit as error:
        return error.code if isinstance(error.code, int) else 0
