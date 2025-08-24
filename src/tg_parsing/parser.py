import os
import json
import ijson
from typing import Generator, List, Tuple
from collections import Counter
from tqdm import tqdm
from .telegram import Message
from .data import ParsedTelegramData

PLAIN_DATA_DIR = 'F:\\tg-chat-exports\\test'
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

def stream_plain_tg_data(filename: str) -> Generator[Message, None, None]:
    """
    Генератор для потокового чтения данных из JSON-файла с помощью ijson.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            yield from ijson.items(f, 'messages.item')
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути {filename}")
        print("Пожалуйста, сначала выполните экспорт эмбеддингов из Milvus.")
        raise
    except json.JSONDecodeError:
        print(f"Ошибка: Не удалось прочитать JSON из файла {filename}.")
        raise

def parse_raw_telegram_data() -> None:
    """
    Обрабатывает "сырые" данные из Telegram, извлекая и обрабатывая необходимые поля,
    и сохраняет их в виде готовых к обработке данных.
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    try:
        total_messages = count_json_items(INPUT_FILE, 'messages.item')
        if total_messages == 0:
            print("В файле не найдено сообщений для обработки.")
            return

        plain_tg_data = stream_plain_tg_data(INPUT_FILE)
        result: list[ParsedTelegramData] = []

        with tqdm(total=total_messages, desc="Parsing Telegram Data") as pbar:
            for item in plain_tg_data:
                if item.get('type') == 'message':
                    text_entities = item.get('text_entities', [])
                    photo = item.get('photo')

                    if text_entities or photo:
                        text = "".join(entity.get('text', '') for entity in text_entities)
                        parsed_data: ParsedTelegramData = {
                            'id': item.get('id'),
                            'date': item.get('date'),
                        }
                        if photo:
                            parsed_data['photo'] = photo
                        if text:
                            parsed_data['text'] = text
                        if text or parsed_data.get('photo'):
                            result.append(parsed_data)
                pbar.update(1)

        with open(PARSED_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Stream processing error: {e}")
        raise

def stream_parsed_tg_data(filename: str) -> Generator[ParsedTelegramData, None, None]:
    """
    Генератор для потокового чтения отфильтрованных данных из JSON-файла.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            yield from ijson.items(f, 'item')
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути {filename}")
        raise
    except json.JSONDecodeError:
        print(f"Ошибка: Не удалось прочитать JSON из файла {filename}.")
        raise

def filter_parsed_telegram_data(
    garbage_phrases_list: List[str],
    garbage_posts_list: List[str],
    exceptions: List[str],
    word_offset: int,
) -> List[Tuple[str, int]]:
    data_base_map = Counter()

    try:
        total_items = count_json_items(PARSED_FILE, 'item')
        if total_items == 0:
            print("Нет данных для фильтрации.")
            return []

        items = stream_parsed_tg_data(PARSED_FILE)
        result: List[ParsedTelegramData] = []

        with tqdm(total=total_items, desc="Filtering Parsed Data") as pbar:
            for item in items:
                if 'text' in item:
                    if any(garbage in item['text'] for garbage in garbage_posts_list):
                        pbar.update(1)
                        continue

                    clean_str = item['text']
                    for garbage in garbage_phrases_list:
                        clean_str = clean_str.replace(garbage, '')

                    clean_str = clean_str.strip()

                    normalized_str_array = [word for word in clean_str.split(' ') if word]

                    for i in range(len(normalized_str_array) - word_offset + 1):
                        entry_slice = normalized_str_array[i:i + word_offset]
                        entry_key = ' '.join(entry_slice)
                        data_base_map[entry_key] += 1

                    result.append({
                        **item,
                        'text': clean_str,
                    })
                pbar.update(1)

        with open(FILTERED_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Stream processing error: {e}")
        raise

    sorted_data_base = data_base_map.most_common(10 + len(exceptions))
    filtered_data = [entry for entry in sorted_data_base if entry[0] not in exceptions]

    return filtered_data

def stream_filtered_tg_data(filename: str) -> Generator[ParsedTelegramData, None, None]:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            yield from ijson.items(f, 'item')
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути {filename}")
        raise
    except json.JSONDecodeError:
        print(f"Ошибка: Не удалось прочитать JSON из файла {filename}.")
        raise
