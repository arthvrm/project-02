from pathlib import Path

from app.models import (
    Category,
    ClassifiedRequest,
    InputRequest,
    Priority,
)
from app.services.report import generate_report


def test_generate_report(tmp_path: Path) -> None:
    results = [
        ClassifiedRequest(
            id="REQ-001",
            category=Category.AUTOMATION,
            target_department="marketing",
            priority=Priority.MEDIUM,
            short_summary="Automate weekly reporting.",
            requested_actions=["Create automation"],
            needs_clarification=False,
        ),
        ClassifiedRequest(
            id="REQ-002",
            category=Category.INTEGRATION,
            target_department=None,
            priority=Priority.HIGH,
            short_summary="Integrate Slack with PlanFix.",
            requested_actions=[
                "Connect Slack",
                "Create PlanFix tickets",
            ],
            needs_clarification=True,
        ),
    ]

    failed_requests = [
        InputRequest(
            id="REQ-003",
            channel="Email",
            timestamp="2026-06-08 10:00",
            raw_text="Failed request",
        )
    ]

    report_path = tmp_path / "report.md"

    generate_report(
        results=results,
        failed_requests=failed_requests,
        total_requests=3,
        file_path=str(report_path),
    )

    report = report_path.read_text(encoding="utf-8")

    assert "# Request Classification Report" in report

    assert "Total requests: 3" in report
    assert "Successfully classified: 2" in report
    assert "Failed: 1" in report

    assert "| автоматизація | 1 |" in report
    assert "| інтеграція | 1 |" in report

    assert "| high | 1 |" in report
    assert "| medium | 1 |" in report

    assert "| marketing | 1 |" in report
    assert "| Unknown | 1 |" in report

    assert "**REQ-002**" in report
    assert "**REQ-003**" in report