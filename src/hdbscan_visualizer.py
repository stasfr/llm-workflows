import os
import pandas as pd
import numpy as np
import umap
import hdbscan
import plotly.express as px
from pymilvus import connections, Collection
from tqdm import tqdm

# Constants
MILVUS_ADDRESS = "http://localhost:19530"
COLLECTION_NAME = "photo_jeldor_cosine_flat"
VECTOR_DIMENSION = 1024
BATCH_SIZE = 1000  # Batch size for fetching data from Milvus
UMAP_N_COMPONENTS = 2
OUTPUT_DIR = os.path.join('.', 'output')


def visualize_hdbscan_clusters(min_cluster_size, min_samples, umap_n_neighbors, umap_min_dist):
    """
    Fetches vectors from Milvus, performs UMAP dimensionality reduction,
    clusters the data using HDBSCAN, and generates an interactive visualization.
    """
    # Generate dynamic output file names
    file_suffix = f"mcs_{min_cluster_size}_ms_{min_samples}_nn_{umap_n_neighbors}_md_{umap_min_dist}"
    output_file = os.path.join(OUTPUT_DIR, f'hdbscan_viz_{file_suffix}.html')
    clusters_output_file = os.path.join(OUTPUT_DIR, f'hdbscan_clusters_{file_suffix}.csv')

    print(f"--- Запуск визуализации со следующими параметрами ---")
    print(f"min_cluster_size: {min_cluster_size}")
    print(f"min_samples: {min_samples}")
    print(f"umap_n_neighbors: {umap_n_neighbors}")
    print(f"umap_min_dist: {umap_min_dist}")
    print(f"----------------------------------------------------")


    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. Connect and fetch all data from Milvus
    connections.connect("default", uri=MILVUS_ADDRESS)
    collection = Collection(COLLECTION_NAME)
    collection.load()
    num_entities = collection.num_entities
    print(f"Коллекция содержит {num_entities} записей.")
    print("--- Этап 1: Загрузка всех векторов из Milvus ---")
    print("Внимание: для работы HDBSCAN все векторы будут загружены в память.")

    all_data = []
    iterator = collection.query_iterator(
        output_fields=["post_id", "text", "vector"],
        expr="post_id > 0",
        batch_size=BATCH_SIZE,
        consistency_level="Eventually"
    )
    with tqdm(total=num_entities, desc="Загрузка данных") as pbar:
        while True:
            result_batch = iterator.next()
            if not result_batch:
                break
            all_data.extend(result_batch)
            pbar.update(len(result_batch))

    df = pd.DataFrame(all_data)
    vectors = np.array(df['vector'].tolist())
    print(f"Загружено {len(df)} векторов.")

    # 2. UMAP transformation
    print("\n--- Этап 2: Уменьшение размерности с помощью UMAP ---")
    reducer = umap.UMAP(
        n_neighbors=umap_n_neighbors,
        min_dist=umap_min_dist,
        n_components=UMAP_N_COMPONENTS,
        random_state=42,
    )
    print("Обучение UMAP и трансформация векторов...")
    embedding_2d = reducer.fit_transform(vectors)
    print("UMAP трансформация завершена.")

    # 3. HDBSCAN Clustering
    print("\n--- Этап 3: Кластеризация с помощью HDBSCAN ---")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric='euclidean',
        cluster_selection_method='eom'  # Stands for Excess of Mass
    )
    clusterer.fit(embedding_2d)
    df['cluster'] = clusterer.labels_
    df[['x', 'y']] = embedding_2d

    n_clusters = len(set(clusterer.labels_)) - (1 if -1 in clusterer.labels_ else 0)
    n_noise = np.sum(clusterer.labels_ == -1)
    print(f"Найдено кластеров: {n_clusters}")
    print(f"Точек (шум): {n_noise}")

    # 4. Visualization
    print("\n--- Этап 4: Создание визуализации ---")
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
    print(f"✅ Визуализация успешно сохранена: {os.path.abspath(output_file)}")

    df_to_save = df[['post_id', 'text', 'cluster']].copy()
    df_to_save.to_csv(clusters_output_file, index=False, encoding='utf-8')
    print(f"✅ Данные по кластерам сохранены: {os.path.abspath(clusters_output_file)}")


if __name__ == "__main__":
    # Тест 1: Сбалансированные параметры (как в руководстве)
    visualize_hdbscan_clusters(min_cluster_size=50, min_samples=5, umap_n_neighbors=15, umap_min_dist=0.1)

    # Тест 2: Больше мелких кластеров
    visualize_hdbscan_clusters(min_cluster_size=25, min_samples=5, umap_n_neighbors=15, umap_min_dist=0.1)

    # Тест 3: Более "консервативная" кластеризация (больше шума)
    visualize_hdbscan_clusters(min_cluster_size=50, min_samples=15, umap_n_neighbors=15, umap_min_dist=0.1)

    # Тест 4: Более плотная визуализация кластеров
    visualize_hdbscan_clusters(min_cluster_size=50, min_samples=5, umap_n_neighbors=15, umap_min_dist=0.0)
