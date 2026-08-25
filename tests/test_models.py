from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models import (
    Category,
    InputRequest,
    Priority,
    RequestClassification,
)


def test_valid_input_request() -> None:
    request = InputRequest(
        id="REQ-001",
        channel="Slack",
        timestamp="2026-06-08 09:14",
        raw_text="Test request",
    )

    assert request.id == "REQ-001"
    assert isinstance(request.timestamp, datetime)


def test_invalid_timestamp() -> None:
    with pytest.raises(ValidationError):
        InputRequest(
            id="REQ-001",
            channel="Slack",
            timestamp="not-a-date",
            raw_text="Test request",
        )


def test_valid_classification() -> None:
    classification = RequestClassification(
        category=Category.AUTOMATION,
        target_department="marketing",
        priority=Priority.MEDIUM,
        short_summary="Automate a manual process.",
        requested_actions=["Create automation"],
        needs_clarification=False,
    )

    assert classification.category == Category.AUTOMATION
    assert classification.priority == Priority.MEDIUM


def test_invalid_category() -> None:
    with pytest.raises(ValidationError):
        RequestClassification(
            category="invalid",
            target_department=None,
            priority="medium",
            short_summary="Test request.",
            requested_actions=[],
            needs_clarification=False,
        )


def test_invalid_priority() -> None:
    with pytest.raises(ValidationError):
        RequestClassification(
            category="автоматизація",
            target_department=None,
            priority="urgent",
            short_summary="Test request.",
            requested_actions=[],
            needs_clarification=False,
        )


def test_extra_fields_are_forbidden() -> None:
    with pytest.raises(ValidationError):
        RequestClassification(
            category="автоматизація",
            target_department=None,
            priority="medium",
            short_summary="Test request.",
            requested_actions=[],
            needs_clarification=False,
            confidence=0.95,
        )