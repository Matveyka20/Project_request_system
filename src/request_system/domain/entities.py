"""Persistence-independent representations of the request system's entities."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AcceptanceOutcome(str, Enum):
    ACCEPTED = "accepted"
    REWORK = "rework"


@dataclass(frozen=True, slots=True)
class User:
    user_id: int | None
    account: str
    name: str
    contacts: str | None = None


@dataclass(frozen=True, slots=True)
class Role:
    role_id: int | None
    name: str


@dataclass(frozen=True, slots=True)
class Status:
    status_id: int | None
    name: str


@dataclass(frozen=True, slots=True)
class Category:
    category_id: int | None
    name: str


@dataclass(frozen=True, slots=True)
class Request:
    request_id: int | None
    request_number: str
    description: str
    applicant_user_id: int
    category_id: int | None
    priority: str | None
    registered_at: datetime


@dataclass(frozen=True, slots=True)
class UserRole:
    user_id: int
    role_id: int


@dataclass(frozen=True, slots=True)
class Comment:
    comment_id: int | None
    request_id: int
    author_user_id: int
    text: str
    is_service: bool
    created_at: datetime


@dataclass(frozen=True, slots=True)
class RequestHistory:
    history_id: int | None
    request_id: int
    actor_user_id: int
    previous_status_id: int | None
    new_status_id: int
    occurred_at: datetime
    explanation: str | None = None


@dataclass(frozen=True, slots=True)
class Assignment:
    assignment_id: int | None
    request_id: int
    assignee_user_id: int
    assigned_by_user_id: int
    assigned_at: datetime
    ended_at: datetime | None = None
    reassignment_reason: str | None = None


@dataclass(frozen=True, slots=True)
class Attachment:
    attachment_id: int | None
    request_id: int
    uploaded_by_user_id: int
    reference: str


@dataclass(frozen=True, slots=True)
class ResultSubmission:
    result_submission_id: int | None
    request_id: int
    executor_user_id: int
    description: str
    submitted_at: datetime


@dataclass(frozen=True, slots=True)
class AcceptanceDecision:
    decision_id: int | None
    result_submission_id: int
    controller_user_id: int
    outcome: AcceptanceOutcome
    comment: str | None
    decided_at: datetime
