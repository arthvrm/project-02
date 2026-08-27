import gspread

from app.models import ClassifiedRequest


HEADERS = [
    "ID",
    "Category",
    "Department",
    "Priority",
    "Summary",
    "Requested Actions",
    "Needs Clarification",
]


def get_worksheet(
    credentials_file: str,
    spreadsheet_id: str,
    worksheet_name: str = "Requests",
):
    client = gspread.service_account(
        filename=credentials_file
    )

    spreadsheet = client.open_by_key(spreadsheet_id)

    try:
        worksheet = spreadsheet.worksheet(
            worksheet_name
        )
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=worksheet_name,
            rows=1000,
            cols=len(HEADERS),
        )
    
    worksheet.append_row(HEADERS)

    return worksheet


def send_results_to_google_sheets(
    results: list[ClassifiedRequest],
    credentials_file: str,
    spreadsheet_id: str,
    worksheet_name: str = "Requests",
) -> int:
    worksheet = get_worksheet(
        credentials_file=credentials_file,
        spreadsheet_id=spreadsheet_id,
        worksheet_name=worksheet_name,
    )

    if not worksheet.get_all_values():
        worksheet.append_row(HEADERS)

    rows = []

    for result in results:
        rows.append(
            [
                result.id,
                result.category.value,
                result.target_department or "error",
                result.priority.value,
                result.short_summary,
                "\n".join(
                    f"• {action}"
                    for action in result.requested_actions
                ),
                result.needs_clarification,
            ]
        )

    if rows:
        worksheet.append_rows(
            rows,
            value_input_option="USER_ENTERED",
        )

    return len(rows)