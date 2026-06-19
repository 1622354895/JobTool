from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class Operation(str, Enum):
    ADD = "add"
    UPDATE = "update"
    FOLLOW_UP = "follow_up"
    QUERY = "query"


@dataclass
class ApplicationDraft:
    company: str = ""
    position: str = ""
    applied_date: date | None = None
    status: str = "已投递"
    job_type: str = ""
    direction: str = ""
    location: str = ""
    channel: str = ""
    priority: str = "中"
    deadline: date | None = None
    next_follow_up: date | None = None
    contact: str = ""
    contact_info: str = ""
    resume_version: str = ""
    salary: str = ""
    url: str = ""
    tags: str = ""
    notes: str = ""


@dataclass
class FollowUpDraft:
    record_type: str = "主动跟进"
    occurred_date: date | None = None
    content: str = ""
    interview_questions: str = ""
    self_review: str = ""
    feedback: str = ""
    next_action: str = ""
    next_date: date | None = None


@dataclass
class ParseResult:
    operation: Operation
    drafts: list[ApplicationDraft] = field(default_factory=list)
    query: dict[str, object] = field(default_factory=dict)
    target: dict[str, str] = field(default_factory=dict)
    changes: dict[str, object] = field(default_factory=dict)
    follow_up: FollowUpDraft | None = None
    warnings: list[str] = field(default_factory=list)
