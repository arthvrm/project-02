from collections import Counter

from app.models import ClassifiedRequest


def generate_report(
    results: list[ClassifiedRequest],
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
        f"**Total requests:** {len(results)}",
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
        count = priority_counts.get(priority, 0)

        report_lines.append(
            f"| {priority} | {count} |"
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

    report = "\n".join(report_lines)

    with open(
        file_path,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(report)