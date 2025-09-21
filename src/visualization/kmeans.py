from config import MILVUS_ADDRESS, STORAGE_FOLDER

import os
import pandas as pd
import numpy as np
from sklearn.cluster import MiniBatchKMeans
import umap
import plotly.express as px
from pymilvus import connections, Collection

from typing import Optional, Callable


def visualize_clusters(
    collection_name: str,
    project_name: str,
    project_snapshot: str,
    umap_sample_size: int = 20000,
    n_clusters: int = 64,
    batch_size: int = 100,
    progress_callback: Optional[Callable[[int, int], None]] = None,
):
    """
    Выполняет кластеризацию K-Means, уменьшает размерность с помощью UMAP и визуализирует результаты.

    Args:
        collection_name (str): Имя коллекции в Milvus для извлечения векторов.
        project_name (str): Имя проекта для структурирования путей вывода.
        project_snapshot (str): Снимок/версия проекта для дальнейшей организации файлов.
        umap_sample_size (int, optional): Количество образцов для обучения UMAP.
                                          Если в коллекции меньше данных, используется
                                          фактическое количество. Defaults to 20000.
        n_clusters (int, optional): Количество кластеров для K-Means. Defaults to 64.
        batch_size (int, optional): Размер пакета для обработки данных. Используется как для
                                    извлечения данных из Milvus, так и для MiniBatchKMeans.
                                    Defaults to 100.
        progress_callback (Optional[Callable[[int, int], None]], optional):
            Обратный вызов для отслеживания прогресса. Принимает текущий шаг и общее
            количество шагов. Defaults to None.
    """
    total_stages = 3

    PROJECT_DIR = os.path.join(
        STORAGE_FOLDER, 'projects', f"{project_name}_{project_snapshot}")

    HTML_OUTPUT_FILE = os.path.join(
        PROJECT_DIR, f'cluster_visualization_{n_clusters}_clusters.html')
    CSV_OUTPUT_FILE = os.path.join(PROJECT_DIR, f'clusters_{n_clusters}.csv')

    connections.connect("default", uri=MILVUS_ADDRESS)
    collection = Collection(collection_name)
    collection.load()

    num_entities = collection.num_entities

    if (num_entities < 20000):
        umap_sample_size = num_entities

    # 1. KMeans Clustering
    kmeans = MiniBatchKMeans(
        n_clusters=n_clusters, random_state=42, batch_size=batch_size, n_init='auto')
    reducer = umap.UMAP(n_components=2, random_state=42)

    sample_vectors = []
    for offset in range(0, umap_sample_size, batch_size):
        limit = min(batch_size, umap_sample_size - len(sample_vectors))
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
            print(
                f"Внимание: в коллекции оказалось меньше данных ({len(sample_vectors)}), чем запрошено для umap_sample_size.")
            break

        sample_vectors.extend([item['vector'] for item in result])

    reducer.fit(np.array(sample_vectors))

    for offset in range(0, num_entities, batch_size):
        result = collection.query(
            output_fields=["vector"],
            limit=batch_size,
            offset=offset,
            expr="post_id > 0",
            consistency_level="Eventually",
        )
        if not result:
            break

        vectors = np.array([item['vector'] for item in result])
        kmeans.partial_fit(vectors)

    if progress_callback:
        progress_callback(1, total_stages)

    # 2. Apply models and collect results
    results = []
    for offset in range(0, num_entities, batch_size):
        result = collection.query(
            output_fields=["post_id", "text", "vector"],
            limit=batch_size,
            offset=offset,
            expr="post_id > 0",
            consistency_level="Eventually",
        )
        if not result:
            break

        df_batch = pd.DataFrame(result)
        vectors = np.array(df_batch['vector'].tolist())

        cluster_labels = kmeans.predict(vectors)
        embedding_2d = reducer.transform(vectors)

        df_batch['cluster'] = cluster_labels
        df_batch[['x', 'y']] = embedding_2d

        results.append(df_batch[['post_id', 'text', 'cluster', 'x', 'y']])

    if not results:
        print("Ошибка: Не удалось обработать данные. Результаты пусты.")
        return

    df = pd.concat(results, ignore_index=True)

    if progress_callback:
        progress_callback(2, total_stages)

    # 3. Visualization and Saving
    df['hover_text'] = df['text'].str.slice(0, 100) + '...'

    fig = px.scatter(
        df,
        x='x',
        y='y',
        color='cluster',
        hover_data={'x': False, 'y': False, 'cluster': True,
                    'post_id': True, 'hover_text': True},
        title=f'Визуализация кластеров сообщений (n={n_clusters})',
        labels={'cluster': 'Кластер', 'hover_text': 'Текст'}
    )
    fig.update_traces(marker=dict(size=5, opacity=0.8))
    fig.update_layout(legend_title_text='Кластеры', xaxis_title="UMAP 1",
                      yaxis_title="UMAP 2", template="plotly_dark")

    fig.write_html(HTML_OUTPUT_FILE)

    df_to_save = df[['post_id', 'text', 'cluster']].copy()
    df_to_save.to_csv(CSV_OUTPUT_FILE, index=False, encoding='utf-8')

    if progress_callback:
        progress_callback(3, total_stages)
