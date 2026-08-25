from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Category(str, Enum):
    AUTOMATION = "автоматизація"
    INTEGRATION = "інтеграція"
    ANALYTICS = "звіт/аналітика"
    BUG_SUPPORT = "баг/підтримка"
    QUESTION = "питання/консультація"
    OUT_OF_SCOPE = "поза скоупом"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class InputRequest(BaseModel):
    id: str
    channel: str
    timestamp: datetime
    raw_text: str = Field(min_length=1)


class RequestClassification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: Category
    target_department: str | None
    priority: Priority
    short_summary: str = Field(min_length=1)
    requested_actions: list[str]
    needs_clarification: bool


class ClassifiedRequest(RequestClassification):
    id: str