from datetime import datetime
import unittest

from request_system.application.services.request_service import (
    CreateRequestCommand,
    RequestRegistrationResult,
)
from request_system.domain.entities import Request, Status
from request_system.presentation.cli import run_registration_cli


class StubRequestService:
    def __init__(self) -> None:
        self.command: CreateRequestCommand | None = None

    def register(self, command: CreateRequestCommand) -> RequestRegistrationResult:
        self.command = command
        return RequestRegistrationResult(
            Request(
                17,
                "REQ-TEST-17",
                "Projector repair",
                2,
                4,
                None,
                datetime.fromisoformat("2026-11-12T12:00:00+00:00"),
            ),
            Status(1, "Новая"),
        )


class MainTests(unittest.TestCase):
    def test_cli_prints_registration_result(self) -> None:
        values = iter(("2", "4", "  Projector repair  "))
        prompts: list[str] = []
        output: list[str] = []
        service = StubRequestService()

        def input_fn(prompt: str) -> str:
            prompts.append(prompt)
            return next(values)

        exit_code = run_registration_cli(service, input_fn=input_fn, output_fn=output.append)

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            prompts,
            ["ID заявителя: ", "ID категории: ", "Описание заявки: "],
        )
        self.assertEqual(
            service.command,
            CreateRequestCommand(2, "  Projector repair  ", 4),
        )
        self.assertEqual(
            output,
            [
                "Регистрация заявки",
                "Заявка зарегистрирована.",
                "Номер: REQ-TEST-17",
                "ID: 17",
                "Дата регистрации: 2026-11-12T12:00:00+00:00",
                "Статус: Новая",
            ],
        )


if __name__ == "__main__":
    unittest.main()
