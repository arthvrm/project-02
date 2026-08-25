from app.models import ClassifiedRequest
from app.services.classifier import RequestClassifier
from app.services.report import generate_report
from app.utils.file_handler import read_requests, save_json


INPUT_FILE = "inputs/input_requests.csv"
OUTPUT_FILE = "results/output.json"
REPORT_FILE = "results/report.md"


def main() -> None:
    requests = read_requests(INPUT_FILE)

    if not requests:
        print("No requests found in CSV file.")
        return

    classifier = RequestClassifier()

    results: list[ClassifiedRequest] = []

    for request in requests:
        print(f"Processing {request.id}...")

        classification = classifier.classify(
            request.raw_text
        )

        if classification is None:
            print(
                f"Skipping {request.id}: "
                "classification failed."
            )
            continue

        results.append(
            ClassifiedRequest(
                id=request.id,
                **classification.model_dump(),
            )
        )

    save_json(
        [
            result.model_dump(mode="json")
            for result in results
        ],
        OUTPUT_FILE,
    )

    generate_report(
        results,
        REPORT_FILE,
    )

    print()
    print(f"Processed: {len(requests)}")
    print(f"Successfully classified: {len(results)}")
    print(f"Output saved to: {OUTPUT_FILE}")
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()