from src.config import STORAGE_FOLDER

import os
import json
import ijson

from typing import Generator, Optional, Callable
from src.modules.parsers.schemas import Message
from src.schemas import ParsedTelegramData

from pydantic import ValidationError

def stream_raw_tg_data(filename: str) -> Generator[dict, None, None]:
    """
    Генератор для потокового чтения данных из JSON-файла с помощью ijson.
    Yields dictionaries.
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

def parse_raw_telegram_data(
    project_name: str,
    project_snapshot: str,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> None:
    """
    Обрабатывает "сырые" данные из Telegram, извлекая, фильтруя и обрабатывая необходимые поля,
    и сохраняет их в виде готовых к обработке данных.
    """

    PHOTOS_DIR = os.path.join(STORAGE_FOLDER, 'photos', project_name)
    PROJECT_DIR = os.path.join(STORAGE_FOLDER, 'projects', f"{project_name}_{project_snapshot}")

    RAW_DATA_FILE = os.path.join(PROJECT_DIR, 'raw_data.json')
    GARBAGE_FILE = os.path.join(PROJECT_DIR, 'garbage.json')
    OUTPUT_FILE = os.path.join(PROJECT_DIR, 'filtered_telegram_data.json')

    garbage_ids = []
    garbage_list = []
    if os.path.exists(GARBAGE_FILE):
        with open(GARBAGE_FILE, 'r', encoding='utf-8') as f:
            try:
                garbage_data = json.load(f)
                garbage_ids = garbage_data.get('garbage_ids', [])
                garbage_list = garbage_data.get('garbage_list', [])
            except json.JSONDecodeError:
                print(f"Warning: Could not decode garbage file at {GARBAGE_FILE}")


    try:
        with open(RAW_DATA_FILE, 'r', encoding='utf-8') as f:
            total_messages = sum(1 for _ in ijson.items(f, 'messages.item'))

        if total_messages == 0:
            print("В файле не найдено сообщений для обработки.")
            return

        raw_tg_data = stream_raw_tg_data(RAW_DATA_FILE)
        result: list[ParsedTelegramData] = []
        garbage_ids_set = set(garbage_ids)
        processed_count = 0

        for item in raw_tg_data:
            if item.get('type') == 'message':
                if item.get('id') in garbage_ids_set:
                    continue
                try:
                    message = Message.model_validate(item)

                    if message.text_entities or message.photo:
                        text = ""
                        if message.text_entities:
                            text = "".join(entity.text for entity in message.text_entities)
                            for garbage in garbage_list:
                                text = text.replace(garbage, '')
                            text = text.strip()

                        parsed_data = ParsedTelegramData(
                            id=message.id,
                            date=message.date,
                        )
                        if message.photo:
                            parsed_data.photo = message.photo
                        if text:
                            parsed_data.text = text

                        if parsed_data.text or parsed_data.photo:
                            result.append(parsed_data)
                except ValidationError as e:
                    pass

            processed_count += 1
            if progress_callback:
                progress_callback(processed_count, total_messages)

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump([item.model_dump(exclude_none=True) for item in result], f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Stream processing error: {e}")
        raise
