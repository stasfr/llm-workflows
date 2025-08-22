import os
import json
import ijson

import os
import json
import ijson
from typing import Generator
from .telegram import Message
from .data import MappedTelegramData

DIR = 'F:\\tg-chat-exports\\test'
INPUT_FILE = os.path.join(DIR, 'result.json')
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
