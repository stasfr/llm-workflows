import os
import json
import ijson

import os
import json
import ijson
from typing import Generator, List, Tuple
from collections import Counter
from .telegram import Message
from .data import MappedTelegramData, ParsedTelegramData

DIR = 'C:\\Users\\stas2\\Code\\llm-workflows\\plain_data'
INPUT_FILE = os.path.join(DIR, 'result.json')
MAPPED_FILE = os.path.join(DIR, 'mapped_telegram_data.json')
PARSED_FILE = os.path.join(DIR, 'parsed_telegram_data.json')
FILTERED_FILE = os.path.join(DIR, 'filtered_telegram_data.json')
OUTPUT_DIR = DIR

def stream_data(filename: str) -> Generator[Message, None, None]:
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

def map_plain_tg_data():
    """
    Обрабатывает "сырые" данные из Telegram, извлекая необходимые поля,
    и сохраняет их в новом JSON-файле.
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    output_filepath = os.path.join(OUTPUT_DIR, 'mapped_telegram_data.json')

    plain_tg_data = stream_data(INPUT_FILE)

    result: list[MappedTelegramData] = []

    for item in plain_tg_data:
        if item.get('type') == 'message':
            mapped_data: MappedTelegramData = {
                'id': item.get('id'),
                'date': item.get('date'),
                'text_entities': item.get('text_entities', [])
            }

            photo = item.get('photo')
            if photo is not None:
                mapped_data['photo'] = photo

            result.append(mapped_data)

    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ Файл {output_filepath} успешно создан!")


def parse_mapped_telegram_data() -> None:
    try:
        with open(MAPPED_FILE, 'r', encoding='utf-8') as f:
            items = ijson.items(f, 'item')
            result: List[ParsedTelegramData] = []
            for item in items:
                if item.get('text_entities') or item.get('photo'):
                    text = "".join(entity.get('text', '') for entity in item.get('text_entities', []))

                    parsed_data: ParsedTelegramData = {
                        'id': item.get('id'),
                        'date': item.get('date'),
                    }

                    if item.get('photo'):
                        parsed_data['photo'] = item.get('photo')

                    if text:
                        parsed_data['text'] = text

                    if text or parsed_data.get('photo'):
                        result.append(parsed_data)

        with open(PARSED_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ Файл {PARSED_FILE} успешно создан!")

    except Exception as e:
        print(f"Stream processing error: {e}")
        raise

def filter_parsed_telegram_data(
    garbage_phrases_list: List[str],
    garbage_posts_list: List[str],
    exceptions: List[str],
    word_offset: int,
) -> List[Tuple[str, int]]:
    data_base_map = Counter()

    try:
        with open(PARSED_FILE, 'r', encoding='utf-8') as f:
            items = ijson.items(f, 'item')
            result: List[ParsedTelegramData] = []

            for item in items:
                if 'text' in item:
                    if any(garbage in item['text'] for garbage in garbage_posts_list):
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

        with open(FILTERED_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ Файл {FILTERED_FILE} успешно создан!")

    except Exception as e:
        print(f"Stream processing error: {e}")
        raise

    sorted_data_base = data_base_map.most_common(10 + len(exceptions))

    filtered_data = [entry for entry in sorted_data_base if entry[0] not in exceptions]

    return filtered_data
