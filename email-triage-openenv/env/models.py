from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Priority(str, Enum):
    URGENT = "urgent"
    NORMAL = "normal"
    LOW = "low"


class Category(str, Enum):
    WORK = "work"
    PERSONAL = "personal"
    SPAM = "spam"
    NEWSLETTER = "newsletter"
    FINANCE = "finance"
    SUPPORT = "support"


class FlagType(str, Enum):
    URGENT = "urgent"
    FOLLOW_UP = "follow_up"
    WAITING = "waiting"
    ACTION_REQUIRED = "action_required"


class ActionType(str, Enum):
    CLASSIFY = "classify"
    ARCHIVE = "archive"
    FLAG = "flag"
    REPLY = "reply"
    DELETE = "delete"
    MARK_READ = "mark_read"
    SEARCH = "search"
    DONE = "done"


# ---------------------------------------------------------------------------
# Core data models
# ---------------------------------------------------------------------------

class Email(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: str
    subject: str
    sender: str
    sender_email: str
    body: str
    timestamp: str
    thread_id: Optional[str] = None
    is_read: bool = False
    labels: List[str] = Field(default_factory=list)
    attachments: List[str] = Field(default_factory=list)


class EmailClassification(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    email_id: str
    priority: Priority
    category: Category
    flag: Optional[FlagType] = None
    requires_reply: bool = False


# ---------------------------------------------------------------------------
# Action model (what the agent sends)
# ---------------------------------------------------------------------------

class Action(BaseModel):
    """Typed action that an agent sends to the environment."""
    model_config = ConfigDict(use_enum_values=True)

    action_type: ActionType

    # classify
    email_id: Optional[str] = None
    priority: Optional[Priority] = None
    category: Optional[Category] = None

    # flag
    flag_type: Optional[FlagType] = None

    # reply
    reply_body: Optional[str] = None
    reply_subject: Optional[str] = None

    # search
    search_query: Optional[str] = None

    # snooze (hours)
    snooze_hours: Optional[int] = None


# ---------------------------------------------------------------------------
# Observation model (what the agent receives)
# ---------------------------------------------------------------------------

class Observation(BaseModel):
    """Full observable state returned after every step."""
    model_config = ConfigDict(use_enum_values=True)

    task_id: str
    task_description: str
    difficulty: str

    inbox: List[Email]
    step_count: int
    max_steps: int

    # accumulated results
    classifications: Dict[str, Any] = Field(default_factory=dict)
    flagged: Dict[str, str] = Field(default_factory=dict)        # email_id -> flag_type
    archived: List[str] = Field(default_factory=list)
    deleted: List[str] = Field(default_factory=list)
    replies: Dict[str, str] = Field(default_factory=dict)        # email_id -> reply body
    search_results: Optional[List[Email]] = None

    message: str = ""                                             # feedback from last action
    done: bool = False
    total_reward: float = 0.0


# ---------------------------------------------------------------------------
# Reward model
# ---------------------------------------------------------------------------

class Reward(BaseModel):
    """Detailed reward breakdown for transparency."""
    model_config = ConfigDict(use_enum_values=True)

    value: float = 0.0
    breakdown: Dict[str, float] = Field(default_factory=dict)
    reason: str = ""


# ---------------------------------------------------------------------------
# State model (internal + observable combined)
# ---------------------------------------------------------------------------

class EnvState(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    task_id: str
    step_count: int = 0
    max_steps: int = 50
    done: bool = False
    total_reward: float = 0.0
    classifications: Dict[str, Any] = Field(default_factory=dict)
    flagged: Dict[str, str] = Field(default_factory=dict)
    archived: List[str] = Field(default_factory=list)
    deleted: List[str] = Field(default_factory=list)
    replies: Dict[str, str] = Field(default_factory=dict)
    action_history: List[Dict[str, Any]] = Field(default_factory=list)
