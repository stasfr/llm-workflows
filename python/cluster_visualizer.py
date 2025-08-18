import json
import os
import pandas as pd
import numpy as np
from sklearn.cluster import MiniBatchKMeans
import umap
import plotly.express as px
import ijson
from tqdm import tqdm
from itertools import islice

# --- Константы ---
INPUT_FILE = os.path.join('..', 'plain_data', 'embeddings.json')
OUTPUT_DIR = os.path.join('..', 'output')
N_CLUSTERS = 64
BATCH_SIZE = 4096  # Размер пакета для обработки данных
UMAP_SAMPLE_SIZE = 20000 # Количество записей для обучения UMAP
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f'cluster_visualization_{N_CLUSTERS}_clusters.html')
CLUSTERS_OUTPUT_FILE = os.path.join(OUTPUT_DIR, f'clusters_{N_CLUSTERS}.csv')

def stream_data(filename):
    """
    Генератор для потокового чтения данных из JSON-файла с помощью ijson.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            yield from ijson.items(f, 'item')
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути {filename}")
        print("Пожалуйста, сначала выполните экспорт эмбеддингов из Milvus.")
        raise
    except json.JSONDecodeError:
        print(f"Ошибка: Не удалось прочитать JSON из файла {filename}.")
        raise


def main():
    """
    Основная функция для загрузки данных, кластеризации, уменьшения размерности и визуализации
    с использованием потоковой обработки для больших наборов данных.
    """
    print("--- Начало работы (оптимизированный скрипт) ---")

    # Проверка существования директории для вывода
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # --- 1. Обучение моделей на данных (без загрузки всего файла в память) ---
    print(f"--- Этап 1: Обучение моделей ---")

    # Инициализация моделей
    kmeans = MiniBatchKMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10, batch_size=BATCH_SIZE)
    reducer = umap.UMAP(n_components=2, random_state=42)

    # Обучение UMAP на выборке данных для определения общей структуры
    print(f"Обучение UMAP на выборке из {UMAP_SAMPLE_SIZE} записей...")
    try:
        sample_vectors = [item['vector'] for item in islice(stream_data(INPUT_FILE), UMAP_SAMPLE_SIZE)]
        if not sample_vectors:
            print("Ошибка: Не удалось прочитать данные для обучения UMAP. Файл пуст?")
            return
        reducer.fit(np.array(sample_vectors))
        print("UMAP успешно обучен.")
    except (FileNotFoundError, json.JSONDecodeError):
        return # Ошибки уже выведены в stream_data

    # Обучение KMeans (MiniBatch) на всех данных в пакетном режиме
    print(f"Обучение MiniBatchKMeans на всех данных (батчи по {BATCH_SIZE})...")
    total_processed = 0
    try:
        with tqdm(desc="Обучение KMeans", unit=" записей") as pbar:
            for batch in pd.read_json(INPUT_FILE, lines=True, chunksize=BATCH_SIZE):
                vectors = np.array(batch['vector'].tolist())
                kmeans.partial_fit(vectors)
                total_processed += len(batch)
                pbar.update(len(batch))
        print(f"KMeans успешно обучен на {total_processed} записях.")
    except ValueError:
         # Fallback for non-lines format
        print("Не удалось прочитать JSON как lines=True, пробую стандартный потоковый метод...")
        try:
            data_generator = stream_data(INPUT_FILE)
            with tqdm(desc="Обучение KMeans", unit=" записей") as pbar:
                 while True:
                    batch_items = list(islice(data_generator, BATCH_SIZE))
                    if not batch_items:
                        break
                    vectors = np.array([item['vector'] for item in batch_items])
                    kmeans.partial_fit(vectors)
                    pbar.update(len(batch_items))
            print(f"KMeans успешно обучен.")
        except (FileNotFoundError, json.JSONDecodeError):
            return


    # --- 2. Применение моделей и сбор результатов ---
    print(f"\n--- Этап 2: Применение моделей и сбор результатов ---")
    results = []
    try:
        data_generator = stream_data(INPUT_FILE)
        with tqdm(desc="Кластеризация и трансформация", unit=" записей") as pbar:
            while True:
                batch_items = list(islice(data_generator, BATCH_SIZE))
                if not batch_items:
                    break

                df_batch = pd.DataFrame(batch_items)
                vectors = np.array(df_batch['vector'].tolist())

                # Применение обученных моделей
                cluster_labels = kmeans.predict(vectors)
                embedding_2d = reducer.transform(vectors)

                df_batch['cluster'] = cluster_labels
                df_batch[['x', 'y']] = embedding_2d

                results.append(df_batch[['post_id', 'text', 'cluster', 'x', 'y']])
                pbar.update(len(batch_items))

        if not results:
            print("Ошибка: Не удалось обработать данные. Результаты пусты.")
            return

        df = pd.concat(results, ignore_index=True)
        print(f"\nОбработано и собрано {len(df)} записей.")

    except (FileNotFoundError, json.JSONDecodeError):
        return

    # --- 3. Визуализация и сохранение ---
    print("--- Этап 3: Создание визуализации и сохранение файлов ---")

    # Обрезаем текст для удобного отображения
    df['hover_text'] = df['text'].str.slice(0, 300) + '...'

    fig = px.scatter(
        df,
        x='x',
        y='y',
        color='cluster',
        hover_data={'x': False, 'y': False, 'cluster': True, 'post_id': True, 'hover_text': True},
        title=f'Визуализация кластеров сообщений (n={N_CLUSTERS})',
        labels={'cluster': 'Кластер', 'hover_text': 'Текст'}
    )
    fig.update_traces(marker=dict(size=5, opacity=0.7))
    fig.update_layout(legend_title_text='Кластеры', xaxis_title="UMAP 1", yaxis_title="UMAP 2")

    # Сохранение HTML
    fig.write_html(OUTPUT_FILE)
    print(f"✅ Визуализация успешно сохранена: {os.path.abspath(OUTPUT_FILE)}")

    # Сохранение CSV
    df_to_save = df[['post_id', 'text', 'cluster']].copy()
    df_to_save.to_csv(CLUSTERS_OUTPUT_FILE, index=False, encoding='utf-8')
    print(f"✅ Данные по кластерам сохранены: {os.path.abspath(CLUSTERS_OUTPUT_FILE)}")

    print("--- Работа завершена ---")


if __name__ == '__main__':
    main()
