import json
import ijson


def count_json_items(filename: str, path: str) -> int:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return sum(1 for _ in ijson.items(f, path))
    except (FileNotFoundError, json.JSONDecodeError):
        return 0
