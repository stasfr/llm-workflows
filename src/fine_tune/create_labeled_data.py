from config import STORAGE_FOLDER

import os
import json
import ijson
from typing import Generator, Dict, Any, List, Optional, Callable


def stream_plain_tg_data(filename: str) -> Generator[Dict[str, Any], None, None]:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            yield from ijson.items(f, 'messages.item')
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути {filename}")
        raise
    except json.JSONDecodeError:
        print(f"Ошибка: Не удалось прочитать JSON из файла {filename}.")
        raise


def create_labeled_data(
    project_name: str,
    project_snapshot: str,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> None:
    # Constants from process_tg_data.py
    PROJECT_DIR = os.path.join(
        STORAGE_FOLDER, 'projects', f"{project_name}_{project_snapshot}")

    RAW_DATA_FILE = os.path.join(PROJECT_DIR, 'raw_data.json')
    GARBAGE_FILE = os.path.join(PROJECT_DIR, 'garbage.json')
    LABELED_FILE = os.path.join(PROJECT_DIR, 'labeled_data.json')

    garbage_ids = []
    garbage_list = []
    if os.path.exists(GARBAGE_FILE):
        with open(GARBAGE_FILE, 'r', encoding='utf-8') as f:
            try:
                garbage_data = json.load(f)
                garbage_ids = garbage_data.get('garbage_ids', [])
                garbage_list = garbage_data.get('garbage_list', [])
            except json.JSONDecodeError:
                print(
                    f"Warning: Could not decode garbage file at {GARBAGE_FILE}")

    try:
        plain_tg_data = stream_plain_tg_data(RAW_DATA_FILE)
        result: List[Dict[str, Any]] = []
        garbage_ids_set = set(garbage_ids)

        for item in plain_tg_data:
            if item.get('type') == 'message':
                text_entities = item.get('text_entities', [])
                text = "".join(entity.get('text', '')
                               for entity in text_entities)

                if text:
                    clean_text = text
                    for garbage in garbage_list:
                        clean_text = clean_text.replace(garbage, '')

                    clean_text = clean_text.strip()

                    if clean_text:
                        message_id = item.get('id')
                        label = 1 if message_id in garbage_ids_set else 0
                        result.append({'text': clean_text, 'result': label})

        with open(LABELED_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Ошибка при обработке потока: {e}")
        raise
