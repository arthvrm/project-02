import csv
import json


def read_requests(file_path: str) -> list[dict[str, str]]:
    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def save_to_json(data: list[dict[str, str]], file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


requests = read_requests("app/input_requests.csv")
save_to_json(requests, "app/input_requests.json")