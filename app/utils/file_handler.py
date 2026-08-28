import csv
import json
import os
from typing import Any

from app.models import InputRequest


def read_requests(file_path: str) -> list[InputRequest]:
    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        
        return [InputRequest.model_validate(row) for row in reader]


def save_json(data: list[dict[str, Any]], file_path: str) -> None:
    directory = os.path.dirname(file_path)

    if directory:
        os.makedirs(directory, exist_ok=True)
    
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
