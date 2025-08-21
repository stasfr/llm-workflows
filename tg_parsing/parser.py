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
OUTPUT_DIR = os.path.join('..', 'output')

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
    # Проверка существования директории для вывода
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    PLAIN_TG_DATA = stream_data(INPUT_FILE)

    for item in PLAIN_TG_DATA:
        print(item['id'])
