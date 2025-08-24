import os
import pandas as pd
import numpy as np
import umap
import hdbscan # New import
import plotly.express as px
from pymilvus import connections, Collection
from tqdm import tqdm

# Constants
MILVUS_ADDRESS = "http://localhost:19530"
COLLECTION_NAME = "filtered_twice_jeldor_cosine_flat"
VECTOR_DIMENSION = 1024

# HDBSCAN parameters
MIN_CLUSTER_SIZE = 50 # The minimum size of a cluster
MIN_SAMPLES = 5       # How conservative the clustering is, a higher value will consider more points as noise

BATCH_SIZE = 1000 # Batch size for fetching data from Milvus
UMAP_N_NEIGHBORS = 15
UMAP_MIN_DIST = 0.1
UMAP_N_COMPONENTS = 2

OUTPUT_DIR = os.path.join('.', 'output')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f'hdbscan_visualization_mcs_{MIN_CLUSTER_SIZE}.html')
CLUSTERS_OUTPUT_FILE = os.path.join(OUTPUT_DIR, f'hdbscan_clusters_mcs_{MIN_CLUSTER_SIZE}.csv')

def visualize_hdbscan_clusters():
    """
    Fetches vectors from Milvus, performs UMAP dimensionality reduction,
    clusters the data using HDBSCAN, and generates an interactive visualization.
    """
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
    with tqdm(total=num_entities, desc="Загрузка данных") as pbar:
        for offset in range(0, num_entities, BATCH_SIZE):
            result = collection.query(
                output_fields=["post_id", "text", "vector"],
                limit=BATCH_SIZE,
                offset=offset,
                expr="post_id > 0",
                consistency_level="Eventually"
            )
            if not result:
                break
            all_data.extend(result)
            pbar.update(len(result))

    df = pd.DataFrame(all_data)
    vectors = np.array(df['vector'].tolist())
    print(f"Загружено {len(df)} векторов.")

    # 2. UMAP transformation
    print("\n--- Этап 2: Уменьшение размерности с помощью UMAP ---")
    reducer = umap.UMAP(
        n_neighbors=UMAP_N_NEIGHBORS,
        min_dist=UMAP_MIN_DIST,
        n_components=UMAP_N_COMPONENTS,
        random_state=42,
    )
    print("Обучение UMAP и трансформация векторов...")
    # It's often better to cluster on the lower-dimensional embedding
    embedding_2d = reducer.fit_transform(vectors)
    print("UMAP трансформация завершена.")

    # 3. HDBSCAN Clustering
    print("\n--- Этап 3: Кластеризация с помощью HDBSCAN ---")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=MIN_CLUSTER_SIZE,
        min_samples=MIN_SAMPLES,
        metric='euclidean',
        cluster_selection_method='eom' # Stands for Excess of Mass
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

    # Convert cluster labels to string for discrete colors in plotly
    # This ensures that noise points (-1) get their own color and are not treated as a numerical value
    df['cluster_str'] = df['cluster'].astype(str)

    # Sort cluster labels for the legend
    sorted_cluster_labels = sorted(df['cluster'].unique())
    sorted_cluster_labels_str = [str(c) for c in sorted_cluster_labels]

    fig = px.scatter(
        df,
        x='x',
        y='y',
        color='cluster_str',
        color_discrete_map={"-1": "grey"}, # Explicitly color noise points
        category_orders={"cluster_str": sorted_cluster_labels_str},
        hover_data={'x': False, 'y': False, 'cluster': True, 'post_id': True, 'hover_text': True},
        title=f'Визуализация кластеров HDBSCAN (min_cluster_size={MIN_CLUSTER_SIZE})',
        labels={'cluster_str': 'Кластер', 'hover_text': 'Текст'}
    )
    fig.update_traces(marker=dict(size=5, opacity=0.8))
    fig.update_layout(legend_title_text='Кластеры', xaxis_title="UMAP 1", yaxis_title="UMAP 2", template="plotly_dark")

    fig.write_html(OUTPUT_FILE)
    print(f"✅ Визуализация успешно сохранена: {os.path.abspath(OUTPUT_FILE)}")

    df_to_save = df[['post_id', 'text', 'cluster']].copy()
    df_to_save.to_csv(CLUSTERS_OUTPUT_FILE, index=False, encoding='utf-8')
    print(f"✅ Данные по кластерам сохранены: {os.path.abspath(CLUSTERS_OUTPUT_FILE)}")

if __name__ == "__main__":
    visualize_hdbscan_clusters()
