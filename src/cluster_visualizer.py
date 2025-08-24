import os
from pymilvus import connections, Collection

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

# Milvus settings
MILVUS_ADDRESS = "http://localhost:19530"
COLLECTION_NAME = "filtered_twice_jeldor_cosine_flat" # DataName_MetricType_IndexType
VECTOR_DIMENSION = 1024 # For intfloat/multilingual-e5-large-instruct

N_CLUSTERS = 64
BATCH_SIZE = 100
UMAP_SAMPLE_SIZE = 20000

OUTPUT_DIR = os.path.join('.', 'output')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f'cluster_visualization_{N_CLUSTERS}_clusters.html')
CLUSTERS_OUTPUT_FILE = os.path.join(OUTPUT_DIR, f'clusters_{N_CLUSTERS}.csv')

def visualize_clusters():
    global UMAP_SAMPLE_SIZE

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    connections.connect("default", uri=MILVUS_ADDRESS)
    collection = Collection(COLLECTION_NAME)
    collection.load()

    num_entities = collection.num_entities

    if (num_entities < 20000):
        UMAP_SAMPLE_SIZE = num_entities

    print(f"--- Этап 1: Обучение моделей ---")

    kmeans = MiniBatchKMeans(n_clusters=N_CLUSTERS, random_state=42, batch_size=BATCH_SIZE, n_init='auto')
    reducer = umap.UMAP(n_components=2, random_state=42)

    sample_vectors = []
    print(f"Сбор данных для обучения UMAP ({UMAP_SAMPLE_SIZE} записей)...")
    for offset in range(0, UMAP_SAMPLE_SIZE, BATCH_SIZE):
        # Рассчитываем, сколько еще нужно записей, чтобы не выйти за UMAP_SAMPLE_SIZE
        limit = min(BATCH_SIZE, UMAP_SAMPLE_SIZE - len(sample_vectors))
        if limit <= 0:
            break

        result = collection.query(
            output_fields=["vector"],
            limit=limit,
            offset=offset,
            expr="post_id > 0",
            consistency_level="Eventually",
        )

        if not result:
            print(f"Внимание: в коллекции оказалось меньше данных ({len(sample_vectors)}), чем запрошено для UMAP_SAMPLE_SIZE.")
            break

        sample_vectors.extend([item['vector'] for item in result])

    reducer.fit(np.array(sample_vectors))

    print(f"Обучение MiniBatchKMeans на всех данных (батчи по {BATCH_SIZE})...")
    with tqdm(total=num_entities, desc="Обучение KMeans") as pbar:
        for offset in range(0, num_entities, BATCH_SIZE):
            result = collection.query(
                output_fields=["vector"],
                limit=BATCH_SIZE,
                offset=offset,
                expr="post_id > 0",
                consistency_level="Eventually",
            )
            if not result:
                break

            vectors = np.array([item['vector'] for item in result])
            kmeans.partial_fit(vectors)
            pbar.update(len(result))
    print(f"KMeans успешно обучен на {pbar.n} записях.")

    print(f"\n--- Этап 2: Применение моделей и сбор результатов ---")
    results = []
    with tqdm(total=num_entities, desc="Кластеризация и трансформация") as pbar:
        for offset in range(0, num_entities, BATCH_SIZE):
            # Предполагаем, что в коллекции есть поля post_id и text
            result = collection.query(
                output_fields=["post_id", "text", "vector"],
                limit=BATCH_SIZE,
                offset=offset,
                expr="post_id > 0",
                consistency_level="Eventually",
            )
            if not result:
                break

            df_batch = pd.DataFrame(result)
            vectors = np.array(df_batch['vector'].tolist())

            # Применение обученных моделей
            cluster_labels = kmeans.predict(vectors)
            embedding_2d = reducer.transform(vectors)

            df_batch['cluster'] = cluster_labels
            df_batch[['x', 'y']] = embedding_2d

            results.append(df_batch[['post_id', 'text', 'cluster', 'x', 'y']])
            pbar.update(len(result))

    if not results:
        print("Ошибка: Не удалось обработать данные. Результаты пусты.")
        return

    df = pd.concat(results, ignore_index=True)
    print(f"\nОбработано и собрано {len(df)} записей.")

    # --- 3. Визуализация и сохранение ---
    print("--- Этап 3: Создание визуализации и сохранение файлов ---")

    # Обрезаем текст для удобного отображения
    df['hover_text'] = df['text'].str.slice(0, 100) + '...'

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


if __name__ == "__main__":
    visualize_clusters()
