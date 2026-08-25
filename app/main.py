import csv
import json
from collections import Counter

from llm import classify_request


def read_requests(file_path: str) -> list[dict[str, str]]:
    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        return list(reader)


def save_results(
    results: list[dict],
    file_path: str,
) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=2,
        )


def generate_report(
    results: list[dict],
    file_path: str,
) -> None:
    category_counts = Counter(
        result["category"]
        for result in results
    )

    priority_counts = Counter(
        result["priority"]
        for result in results
    )

    department_counts = Counter(
        result["target_department"] or "Unknown"
        for result in results
    )

    clarification_requests = [
        result
        for result in results
        if result["needs_clarification"]
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
        report_lines.append(f"| {category} | {count} |")

    report_lines.extend(
        [
            "",
            "## By Priority",
            "",
            "| Priority | Count |",
            "|---|---:|",
        ]
    )

    priority_order = ["high", "medium", "low"]

    for priority in priority_order:
        count = priority_counts.get(priority, 0)
        report_lines.append(f"| {priority} | {count} |")

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
        report_lines.append(f"| {department} | {count} |")

    report_lines.extend(
        [
            "",
            "## Requests Requiring Clarification",
            "",
        ]
    )

    if clarification_requests:
        for request in clarification_requests:
            request_id = request["id"]
            summary = request["short_summary"]

            report_lines.append(
                f"- **{request_id}** — {summary}"
            )
    else:
        report_lines.append("No requests require clarification.")

    report = "\n".join(report_lines)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(report)


def main() -> None:
    requests = read_requests("app/input_requests.csv")

    if not requests:
        print("No requests found in CSV file.")
        return

    results = []

    for request in requests:
        request_id = request["id"]

        print(f"Processing {request_id}...")

        classification = classify_request(
            request["raw_text"]
        )

        if classification is None:
            print(
                f"Skipping {request_id}: "
                "classification failed."
            )
            continue

        result = {
            "id": request_id,
            **classification.model_dump(mode="json"),
        }

        results.append(result)

    save_results(results, "output.json")
    generate_report(results, "report.md")

    print()
    print(f"Processed: {len(requests)}")
    print(f"Successfully classified: {len(results)}")
    print("Output saved to: output.json")
    print("Report saved to: report.md")


if __name__ == "__main__":
    main()