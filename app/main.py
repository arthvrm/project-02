import csv

from llm import classify_request


def read_requests(file_path: str) -> list[dict[str, str]]:
    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        return list(reader)


def main() -> None:
    requests = read_requests("app/input_requests.csv")

    if not requests:
        print("No requests found in CSV file.")
        return

    first_request = requests[0]

    print(f"Processing request: {first_request['id']}")
    print(f"Text: {first_request['raw_text']}")
    print()

    result = classify_request(first_request["raw_text"])

    if result is None:
        print("Request classification failed.")
        return

    print("Classification:")
    print(result.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()