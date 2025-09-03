import os
import json
import ijson
from typing import List, Dict, Any

from config import STORAGE_FOLDER

def upsample_positive_records(
    project_name: str,
    project_snapshot: str,
    upsample_factor: int = 10,
) -> None:
    PROJECT_DIR = os.path.join(STORAGE_FOLDER, 'projects', f"{project_name}_{project_snapshot}")
    LABELED_FILE = os.path.join(PROJECT_DIR, 'labeled_data.json')
    UPSAMPLED_FILE = os.path.join(PROJECT_DIR, 'upsampled_labeled_data.json')

    positive_records: List[Dict[str, Any]] = []
    try:
        with open(LABELED_FILE, 'r', encoding='utf-8') as f:
            print(f"Чтение файла: {LABELED_FILE}")
            for record in ijson.items(f, 'item'):
                if record.get('result') == 1:
                    positive_records.append(record)
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден {LABELED_FILE}")
        return
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")
        return

    if not positive_records:
        print("Не найдено записей с result == 1.")
        return

    print(f"Найдено {len(positive_records)} записей с result == 1.")

    upsampled_data: List[Dict[str, Any]] = []
    for record in positive_records:
        upsampled_data.extend([record] * upsample_factor)

    try:
        os.makedirs(PROJECT_DIR, exist_ok=True)

        with open(UPSAMPLED_FILE, 'w', encoding='utf-8') as f:
            json.dump(upsampled_data, f, ensure_ascii=False, indent=2)

        print(f"Создан файл с апсемплингом: {UPSAMPLED_FILE}")

    except Exception as e:
        print(f"Произошла ошибка при записи файла: {e}")
