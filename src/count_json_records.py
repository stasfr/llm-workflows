import os
import json
import ijson

PLAIN_DATA_DIR = 'F:\\tg-chat-exports\\jeldor'
INPUT_FILE = os.path.join(PLAIN_DATA_DIR, 'result.json')

WORKING_DIR = './output'
PARSED_FILE = os.path.join(WORKING_DIR, 'parsed_telegram_data.json')
FILTERED_FILE = os.path.join(WORKING_DIR, 'filtered_telegram_data.json')
LABEL_FILE = os.path.join(WORKING_DIR, 'labeled_data.json')
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

    print(f'Counting items in {LABEL_FILE}...')
    try:
        with open(LABEL_FILE, 'r', encoding='utf-8') as f:
            total_labeled = 0
            result_0_count = 0
            result_1_count = 0
            # Assuming the file contains a JSON array of objects
            for record in ijson.items(f, 'item'):
                total_labeled += 1
                if 'result' in record:
                    if record['result'] == 0:
                        result_0_count += 1
                    elif record['result'] == 1:
                        result_1_count += 1

        print(f'Total items: {total_labeled}')
        print(f'Items with result == 0: {result_0_count}')
        print(f'Items with result == 1: {result_1_count}')

    except FileNotFoundError:
        print(f'{LABEL_FILE} not found.')
    except Exception as e:
        print(f'An error occurred: {e}')
