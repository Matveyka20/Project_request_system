import ast
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import tempfile
import unittest

from request_system.domain.entities import (
    AcceptanceDecision,
    AcceptanceOutcome,
    Assignment,
    Attachment,
    Category,
    Comment,
    Request,
    ResultSubmission,
    Role,
    Status,
    User,
    UserRole,
)
from request_system.application.services.request_service import (
    CreateRequestCommand,
    RequestService,
)
from request_system.infrastructure.database.sqlite import SQLiteDatabase
from request_system.application.ports.persistence import PersistenceError


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "sql" / "schema.sql"
SEED_PATH = ROOT / "docs" / "sql" / "seed.sql"
NOW = datetime(2025, 1, 2, 3, 4, tzinfo=timezone.utc)


class PersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.database_path = Path(self.temporary_directory.name) / "requests.sqlite3"
        self.database = SQLiteDatabase(self.database_path, SCHEMA_PATH)
        self.database.initialize()

        with self.database.unit_of_work() as unit_of_work:
            self.applicant = unit_of_work.users.add(
                User(None, "applicant", "Applicant", "applicant@example.test")
            )
            self.operator = unit_of_work.users.add(User(None, "operator", "Operator"))
            self.executor = unit_of_work.users.add(User(None, "executor", "Executor"))
            self.controller = unit_of_work.users.add(User(None, "controller", "Controller"))
            self.role = unit_of_work.roles.add(Role(None, "applicant"))
            self.status = unit_of_work.statuses.add(Status(None, "new"))
            self.category = unit_of_work.categories.add(Category(None, "repair"))
            self.user_role = unit_of_work.user_roles.add(
                UserRole(self.applicant.user_id, self.role.role_id)
            )
            self.request, self.initial_history = (
                unit_of_work.requests.create_with_initial_status(
                    Request(
                        None,
                        "REQ-2025-0001",
                        "Repair the classroom projector",
                        self.applicant.user_id,
                        self.category.category_id,
                        None,
                        NOW,
                    ),
                    actor_user_id=self.applicant.user_id,
                    previous_status_id=None,
                    new_status_id=self.status.status_id,
                    occurred_at=NOW,
                )
            )
            self.comment = unit_of_work.comments.add(
                Comment(
                    None,
                    self.request.request_id,
                    self.applicant.user_id,
                    "The projector does not turn on.",
                    False,
                    NOW + timedelta(minutes=1),
                )
            )
            self.assignment = unit_of_work.assignments.add(
                Assignment(
                    None,
                    self.request.request_id,
                    self.executor.user_id,
                    self.operator.user_id,
                    NOW + timedelta(minutes=2),
                )
            )
            self.attachment = unit_of_work.attachments.add(
                Attachment(
                    None,
                    self.request.request_id,
                    self.applicant.user_id,
                    "uploads/projector.jpg",
                )
            )
            self.result = unit_of_work.result_submissions.add(
                ResultSubmission(
                    None,
                    self.request.request_id,
                    self.executor.user_id,
                    "Replaced the power cable.",
                    NOW + timedelta(hours=1),
                )
            )
            self.decision = unit_of_work.acceptance_decisions.add(
                AcceptanceDecision(
                    None,
                    self.result.result_submission_id,
                    self.controller.user_id,
                    AcceptanceOutcome.ACCEPTED,
                    None,
                    NOW + timedelta(hours=2),
                )
            )

    def test_round_trips_entities_for_every_schema_table(self) -> None:
        expected_tables = {
            "Users",
            "Roles",
            "Statuses",
            "Categories",
            "Requests",
            "UserRoles",
            "Comments",
            "RequestHistory",
            "Assignments",
            "Attachments",
            "ResultSubmissions",
            "AcceptanceDecisions",
        }
        cases = (
            ("users", self.applicant.user_id, self.applicant),
            ("roles", self.role.role_id, self.role),
            ("statuses", self.status.status_id, self.status),
            ("categories", self.category.category_id, self.category),
            ("requests", self.request.request_id, self.request),
            (
                "user_roles",
                (self.user_role.user_id, self.user_role.role_id),
                self.user_role,
            ),
            ("comments", self.comment.comment_id, self.comment),
            ("request_history", self.initial_history.history_id, self.initial_history),
            ("assignments", self.assignment.assignment_id, self.assignment),
            ("attachments", self.attachment.attachment_id, self.attachment),
            ("result_submissions", self.result.result_submission_id, self.result),
            (
                "acceptance_decisions",
                self.decision.decision_id,
                self.decision,
            ),
        )

        with self.database.unit_of_work() as unit_of_work:
            for repository_name, key, expected in cases:
                repository = getattr(unit_of_work, repository_name)
                self.assertEqual(repository.get(key), expected, repository_name)
                self.assertIn(expected, repository.list_all(), repository_name)

        connection = sqlite3.connect(self.database_path)
        try:
            actual_tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
        finally:
            connection.close()
        self.assertEqual(actual_tables, expected_tables)

    def test_seed_script_creates_consistent_sample_database(self) -> None:
        seed_database_path = Path(self.temporary_directory.name) / "sample.sqlite3"
        seed_database = SQLiteDatabase(seed_database_path, SCHEMA_PATH)
        seed_database.initialize()

        connection = sqlite3.connect(seed_database_path)
        try:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.executescript(SEED_PATH.read_text(encoding="utf-8"))
            counts = {
                table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in ("Users", "Categories", "Statuses", "Requests")
            }
            self.assertGreaterEqual(counts["Users"], 4)
            self.assertGreaterEqual(counts["Categories"], 4)
            self.assertGreaterEqual(counts["Statuses"], 4)
            self.assertGreaterEqual(counts["Requests"], 10)
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM RequestHistory WHERE previous_status_id IS NULL"
                ).fetchone()[0],
                counts["Requests"],
            )
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
        finally:
            connection.close()

    def test_update_and_delete(self) -> None:
        updated_user = replace(self.applicant, name="Updated applicant")
        role_key = (self.user_role.user_id, self.user_role.role_id)

        with self.database.unit_of_work() as unit_of_work:
            self.assertTrue(unit_of_work.users.update(updated_user))
            self.assertEqual(unit_of_work.users.get(self.applicant.user_id), updated_user)
            self.assertTrue(unit_of_work.user_roles.update(self.user_role))
            self.assertTrue(unit_of_work.user_roles.delete(role_key))
            self.assertIsNone(unit_of_work.user_roles.get(role_key))
            self.assertFalse(unit_of_work.user_roles.delete(role_key))

        with self.database.unit_of_work() as unit_of_work:
            self.assertEqual(unit_of_work.users.get(self.applicant.user_id), updated_user)

    def test_request_service_persists_through_sqlite_ports(self) -> None:
        with self.database.unit_of_work() as unit_of_work:
            unit_of_work.statuses.add(Status(None, "Новая"))

        service = RequestService(
            self.database.unit_of_work,
            clock=lambda: NOW + timedelta(minutes=10),
            request_number_factory=lambda: "REQ-SERVICE-1",
        )
        result = service.register(
            CreateRequestCommand(
                self.applicant.user_id,
                "  Register through the application service  ",
                self.category.category_id,
            )
        )

        with self.database.unit_of_work() as unit_of_work:
            stored_request = unit_of_work.requests.get(result.request.request_id)
            self.assertEqual(stored_request, result.request)
            matching_history = [
                event
                for event in unit_of_work.request_history.list_all()
                if event.request_id == result.request.request_id
            ]
            self.assertEqual(len(matching_history), 1)
            self.assertIsNone(matching_history[0].previous_status_id)
            self.assertEqual(matching_history[0].new_status_id, result.initial_status.status_id)

    def test_request_and_initial_history_are_atomic(self) -> None:
        failed_request = Request(
            None,
            "REQ-ROLLBACK",
            "This request must roll back",
            self.applicant.user_id,
            self.category.category_id,
            None,
            NOW,
        )

        with self.assertRaises(PersistenceError) as raised:
            with self.database.unit_of_work() as unit_of_work:
                unit_of_work.requests.create_with_initial_status(
                    failed_request,
                    actor_user_id=self.applicant.user_id,
                    previous_status_id=None,
                    new_status_id=999_999,
                    occurred_at=NOW,
                )
        self.assertIsInstance(raised.exception.__cause__, sqlite3.IntegrityError)

        with self.database.unit_of_work() as unit_of_work:
            requests = unit_of_work.requests.list_all()
            self.assertNotIn("REQ-ROLLBACK", [request.request_number for request in requests])

    def test_foreign_keys_and_schema_checks_are_enforced(self) -> None:
        with self.assertRaises(PersistenceError):
            with self.database.unit_of_work() as unit_of_work:
                unit_of_work.comments.add(
                    Comment(None, 999_999, self.applicant.user_id, "Invalid FK", False, NOW)
                )

        with self.assertRaises(PersistenceError):
            with self.database.unit_of_work() as unit_of_work:
                unit_of_work.acceptance_decisions.add(
                    AcceptanceDecision(
                        None,
                        self.result.result_submission_id,
                        self.controller.user_id,
                        AcceptanceOutcome.REWORK,
                        "   ",
                        NOW,
                    )
                )

        with self.assertRaises(PersistenceError):
            with self.database.unit_of_work() as unit_of_work:
                unit_of_work.assignments.add(
                    Assignment(
                        None,
                        self.request.request_id,
                        self.executor.user_id,
                        self.operator.user_id,
                        NOW + timedelta(minutes=3),
                    )
                )

    def test_database_connection_errors_use_persistence_error(self) -> None:
        invalid_database = SQLiteDatabase(self.temporary_directory.name, SCHEMA_PATH)
        with self.assertRaises(PersistenceError) as raised:
            invalid_database.unit_of_work()
        self.assertIsInstance(raised.exception.__cause__, sqlite3.Error)

    def test_unit_of_work_rolls_back_on_error(self) -> None:
        with self.assertRaises(RuntimeError):
            with self.database.unit_of_work() as unit_of_work:
                unit_of_work.roles.add(Role(None, "temporary"))
                raise RuntimeError("abort transaction")

        with self.database.unit_of_work() as unit_of_work:
            self.assertEqual(
                [role.name for role in unit_of_work.roles.list_all()],
                ["applicant"],
            )

    def test_domain_and_ports_do_not_import_infrastructure_or_sqlite(self) -> None:
        source_roots = (
            ROOT / "src" / "request_system" / "domain",
            ROOT / "src" / "request_system" / "application",
        )
        for source_root in source_roots:
            for path in source_root.rglob("*.py"):
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported = [alias.name for alias in node.names]
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imported = [node.module]
                    else:
                        continue
                    for module in imported:
                        self.assertNotEqual(module.split(".")[0], "sqlite3", str(path))
                        self.assertNotIn("infrastructure", module.split("."), str(path))


if __name__ == "__main__":
    unittest.main()
