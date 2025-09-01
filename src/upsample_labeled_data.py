import os
import json
import ijson

# Определяем константы на основе предоставленного скрипта
WORKING_DIR = './output'
LABEL_FILE = os.path.join(WORKING_DIR, 'labeled_data.json')
UPSAMPLED_FILE = os.path.join(WORKING_DIR, 'upsampled_labeled_data.json')

def upsample_positive_records():
    """
    Читает файл LABEL_FILE, находит все элементы с 'result' == 1,
    и записывает каждый из них по 10 раз в новый JSON-файл.
    """
    positive_records = []
    try:
        with open(LABEL_FILE, 'r', encoding='utf-8') as f:
            print(f"Чтение файла: {LABEL_FILE}")
            # Итеративно читаем объекты из JSON-массива
            for record in ijson.items(f, 'item'):
                if record.get('result') == 1:
                    positive_records.append(record)
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден {LABEL_FILE}")
        return
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")
        return

    if not positive_records:
        print("Не найдено записей с result == 1.")
        return

    print(f"Найдено {len(positive_records)} записей с result == 1.")

    upsampled_data = []
    for record in positive_records:
        upsampled_data.extend([record] * 10)

    try:
        # Убедимся, что директория для вывода существует
        os.makedirs(WORKING_DIR, exist_ok=True)

        print(f"Запись данных в файл: {UPSAMPLED_FILE}")
        with open(UPSAMPLED_FILE, 'w', encoding='utf-8') as f:
            json.dump(upsampled_data, f, ensure_ascii=False, indent=2)

        print(f"Файл успешно создан: {UPSAMPLED_FILE}")
        print(f"Общее количество записей в новом файле: {len(upsampled_data)}")

    except Exception as e:
        print(f"Произошла ошибка при записи файла: {e}")

if __name__ == '__main__':
    upsample_positive_records()
