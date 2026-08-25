from collections import Counter

from app.models import ClassifiedRequest, InputRequest


def generate_report(
    results: list[ClassifiedRequest],
    failed_requests: list[InputRequest],
    total_requests: int,
    file_path: str,
) -> None:
    category_counts = Counter(
        result.category.value
        for result in results
    )

    priority_counts = Counter(
        result.priority.value
        for result in results
    )

    department_counts = Counter(
        result.target_department or "Unknown"
        for result in results
    )

    clarification_requests = [
        result
        for result in results
        if result.needs_clarification
    ]

    report_lines = [
        "# Request Classification Report",
        "",
        "## Processing Statistics",
        "",
        f"- Total requests: {total_requests}",
        f"- Successfully classified: {len(results)}",
        f"- Failed: {len(failed_requests)}",
        "",
        "## By Category",
        "",
        "| Category | Count |",
        "|---|---:|",
    ]

    for category, count in category_counts.most_common():
        report_lines.append(
            f"| {category} | {count} |"
        )

    report_lines.extend(
        [
            "",
            "## By Priority",
            "",
            "| Priority | Count |",
            "|---|---:|",
        ]
    )

    for priority in ("high", "medium", "low"):
        report_lines.append(
            f"| {priority} | "
            f"{priority_counts.get(priority, 0)} |"
        )

    report_lines.extend(
        [
            "",
            "## By Department",
            "",
            "| Department | Count |",
            "|---|---:|",
        ]
    )

    for department, count in department_counts.most_common():
        report_lines.append(
            f"| {department} | {count} |"
        )

    report_lines.extend(
        [
            "",
            "## Requests Requiring Clarification",
            "",
        ]
    )

    if clarification_requests:
        for request in clarification_requests:
            report_lines.append(
                f"- **{request.id}** — "
                f"{request.short_summary}"
            )
    else:
        report_lines.append(
            "No requests require clarification."
        )

    report_lines.extend(
        [
            "",
            "## Failed Requests",
            "",
        ]
    )

    if failed_requests:
        for request in failed_requests:
            report_lines.append(
                f"- **{request.id}** — "
                f"Classification failed."
            )
    else:
        report_lines.append(
            "No requests failed classification."
        )

    report = "\n".join(report_lines)

    with open(
        file_path,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(report)