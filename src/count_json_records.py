import os
import json
import ijson

PLAIN_DATA_DIR = 'F:\\tg-chat-exports\\jeldor'
INPUT_FILE = os.path.join(PLAIN_DATA_DIR, 'result.json')

WORKING_DIR = './output'
PARSED_FILE = os.path.join(WORKING_DIR, 'parsed_telegram_data.json')
FILTERED_FILE = os.path.join(WORKING_DIR, 'filtered_telegram_data.json')
OUTPUT_DIR = WORKING_DIR

def count_json_items(filename: str, path: str) -> int:
    """
    Подсчитывает количество элементов в JSON-файле по указанному пути.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return sum(1 for _ in ijson.items(f, path))
    except (FileNotFoundError, json.JSONDecodeError):
        return 0


if __name__ == '__main__':
    print(f'Counting items in {INPUT_FILE}...')
    total_items = count_json_items(INPUT_FILE, 'messages.item')
    print(f'Total items: {total_items}')

    print(f'Counting items in {PARSED_FILE}...')
    parsed_items = count_json_items(PARSED_FILE, 'item')
    print(f'Parsed items: {parsed_items}')

    print(f'Counting items in {FILTERED_FILE}...')
    filtered_items = count_json_items(FILTERED_FILE, 'item')
    print(f'Filtered items: {filtered_items}')
