import os
import json
import ijson
from tqdm import tqdm
from typing import Generator, Dict, Any, List
import consts

# Constants from process_tg_data.py
PLAIN_DATA_DIR = 'F:\\tg-chat-exports\\jeldor'
INPUT_FILE = os.path.join(PLAIN_DATA_DIR, 'result.json')
WORKING_DIR = './output'
LABELED_FILE = os.path.join(WORKING_DIR, 'labeled_data.json')

def count_json_items(filename: str, path: str) -> int:
    """
    Подсчитывает количество элементов в JSON-файле по указанному пути.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return sum(1 for _ in ijson.items(f, path))
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def stream_plain_tg_data(filename: str) -> Generator[Dict[str, Any], None, None]:
    """
    Генератор для потокового чтения данных из JSON-файла с помощью ijson.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            yield from ijson.items(f, 'messages.item')
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути {filename}")
        raise
    except json.JSONDecodeError:
        print(f"Ошибка: Не удалось прочитать JSON из файла {filename}.")
        raise

def create_labeled_data() -> None:
    """
    Создает размеченный набор данных из "сырых" данных Telegram.
    Для каждого сообщения, содержащего текст, определяется метка "мусор" (1) или "не мусор" (0).
    """
    if not os.path.exists(WORKING_DIR):
        os.makedirs(WORKING_DIR)

    try:
        total_messages = count_json_items(INPUT_FILE, 'messages.item')
        if total_messages == 0:
            print("В файле не найдено сообщений для обработки.")
            return

        plain_tg_data = stream_plain_tg_data(INPUT_FILE)
        result: List[Dict[str, Any]] = []
        garbage_ids_set = set(consts.GARBAGE_IDS)

        with tqdm(total=total_messages, desc="Creating Labeled Data") as pbar:
            for item in plain_tg_data:
                if item.get('type') == 'message':
                    text_entities = item.get('text_entities', [])
                    text = "".join(entity.get('text', '') for entity in text_entities)

                    if text:
                        clean_text = text
                        for garbage in consts.GARBAGE_LIST:
                            clean_text = clean_text.replace(garbage, '')

                        clean_text = clean_text.strip()

                        if clean_text:
                            message_id = item.get('id')
                            label = 1 if message_id in garbage_ids_set else 0
                            result.append({'text': clean_text, 'result': label})

                pbar.update(1)

        with open(LABELED_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"Размеченные данные сохранены в {LABELED_FILE}")

    except Exception as e:
        print(f"Ошибка при обработке потока: {e}")
        raise

if __name__ == "__main__":
    create_labeled_data()
