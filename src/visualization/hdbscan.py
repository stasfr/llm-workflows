from config import MILVUS_ADDRESS, STORAGE_FOLDER

import os
import pandas as pd
import numpy as np
import umap
import hdbscan
import plotly.express as px
from pymilvus import connections, Collection

from typing import Optional, Callable

def visualize_hdbscan_clusters(
    collection_name: str,
    project_name: str,
    project_snapshot: str,
    min_cluster_size: int,
    min_samples: int,
    umap_n_neighbors: int,
    umap_min_dist: float,
    umap_n_components: int = 2,
    batch_size: int = 1000,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> None:
    """
    Визуализирует кластеры, полученные с помощью HDBSCAN, и сохраняет результаты.

    Args:
        collection_name (str): Имя коллекции в Milvus, из которой извлекаются данные.
        project_name (str): Имя проекта, используемое для организации хранения файлов.
        project_snapshot (str): Снимок/версия проекта для дальнейшей организации файлов.
        min_cluster_size (int): Минимальный размер кластера для HDBSCAN. Определяет минимальное
                                количество точек, которое может считаться кластером.
        min_samples (int): Параметр min_samples для HDBSCAN. Определяет, сколько соседей
                           должна иметь точка, чтобы считаться ядром кластера. Более высокие
                           значения делают кластеризацию более консервативной.
        umap_n_neighbors (int): Количество соседей для UMAP. Влияет на локальную и глобальную
                                структуру вложения. Большие значения учитывают больше глобальной
                                структуры.
        umap_min_dist (float): Минимальное расстояние между точками в UMAP. Контролирует,
                               насколько плотно UMAP может упаковывать точки. Низкие значения
                               оптимизируют локальную структуру, высокие - глобальную.
        umap_n_components (int): Количество компонент (размерность) для вложения UMAP.
                                 Обычно 2 для 2D-визуализации.
        batch_size (int, optional): Размер пакета для извлечения данных из Milvus.
                                    Defaults to 1000.
        progress_callback (Optional[Callable[[int, int], None]], optional):
            Обратный вызов для отслеживания прогресса. Принимает текущий шаг и общее
            количество шагов. Defaults to None.
    """
    total_stages = 4

    PROJECT_DIR = os.path.join(STORAGE_FOLDER, 'projects', f"{project_name}_{project_snapshot}")

    # Generate dynamic output file names
    file_suffix = f"mcs_{min_cluster_size}_ms_{min_samples}_nn_{umap_n_neighbors}_md_{umap_min_dist}"
    output_file = os.path.join(PROJECT_DIR, f'hdbscan_viz_{file_suffix}.html')
    clusters_output_file = os.path.join(PROJECT_DIR, f'hdbscan_clusters_{file_suffix}.csv')


    # 1. Connect and fetch all data from Milvus
    connections.connect("default", uri=MILVUS_ADDRESS)
    collection = Collection(collection_name)
    collection.load()

    all_data = []
    iterator = collection.query_iterator(
        output_fields=["post_id", "text", "vector"],
        expr="post_id > 0",
        batch_size=batch_size,
        consistency_level="Eventually"
    )
    while True:
        result_batch = iterator.next()
        if not result_batch:
            break
        all_data.extend(result_batch)

    df = pd.DataFrame(all_data)
    vectors = np.array(df['vector'].tolist())

    if progress_callback:
        progress_callback(1, total_stages)

    # 2. UMAP transformation
    reducer = umap.UMAP(
        n_neighbors=umap_n_neighbors,
        min_dist=umap_min_dist,
        n_components=umap_n_components,
        random_state=42,
    )
    embedding_2d = reducer.fit_transform(vectors)

    if progress_callback:
        progress_callback(2, total_stages)

    # 3. HDBSCAN Clustering
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric='euclidean',
        cluster_selection_method='eom'
    )
    clusterer.fit(embedding_2d)
    df['cluster'] = clusterer.labels_
    df[['x', 'y']] = embedding_2d

    n_clusters = len(set(clusterer.labels_)) - (1 if -1 in clusterer.labels_ else 0)
    n_noise = np.sum(clusterer.labels_ == -1)

    if progress_callback:
        progress_callback(3, total_stages)

    # 4. Visualization
    df['hover_text'] = df['text'].str.slice(0, 100) + '...'
    df['cluster_str'] = df['cluster'].astype(str)

    sorted_cluster_labels = sorted(df['cluster'].unique())
    sorted_cluster_labels_str = [str(c) for c in sorted_cluster_labels]

    title = (f'Визуализация HDBSCAN (mcs={min_cluster_size}, ms={min_samples}, '
             f'nn={umap_n_neighbors}, md={umap_min_dist})')

    fig = px.scatter(
        df,
        x='x',
        y='y',
        color='cluster_str',
        color_discrete_map={"-1": "grey"},
        category_orders={"cluster_str": sorted_cluster_labels_str},
        hover_data={'x': False, 'y': False, 'cluster': True, 'post_id': True, 'hover_text': True},
        title=title,
        labels={'cluster_str': 'Кластер', 'hover_text': 'Текст'}
    )
    fig.update_traces(marker=dict(size=5, opacity=0.8))
    fig.update_layout(legend_title_text='Кластеры', xaxis_title="UMAP 1", yaxis_title="UMAP 2",
                      template="plotly_dark")

    fig.write_html(output_file)

    df_to_save = df[['post_id', 'text', 'cluster']].copy()
    df_to_save.to_csv(clusters_output_file, index=False, encoding='utf-8')

    if progress_callback:
        progress_callback(4, total_stages)
