import json
import csv

from llm import classify_request


def read_requests(file_path: str) -> list[dict[str, str]]:
    with open(file_path, "r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


requests = read_requests("app/input_requests.csv")

first_request = requests[0]

result = classify_request(first_request["raw_text"])

print(result)