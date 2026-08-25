import csv
import json

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


def main() -> None:
    requests = read_requests("app/input_requests.csv")

    if not requests:
        print("No requests found in CSV file.")
        return

    results = []

    for request in requests:
        request_id = request["id"]

        print(f"Processing {request_id}...")

        classification = classify_request(request["raw_text"])

        if classification is None:
            print(f"Skipping {request_id}: classification failed.")
            continue

        result = {
            "id": request_id,
            **classification.model_dump(mode="json"),
        }

        results.append(result)

    save_results(results, "output.json")

    print()
    print(f"Processed: {len(requests)}")
    print(f"Successfully classified: {len(results)}")
    print(f"Output saved to: output.json")


if __name__ == "__main__":
    main()