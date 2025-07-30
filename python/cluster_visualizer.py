import json
import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import umap
import plotly.express as px

# --- Константы ---
INPUT_FILE = os.path.join('..', 'plain_data', 'embeddings.json')
OUTPUT_DIR = os.path.join('..', 'output')
N_CLUSTERS = 64 # Можете изменить это значение, чтобы найти оптимальное количество кластеров
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f'cluster_visualization_{N_CLUSTERS}_clusters.html')  # Можете изменить это значение, чтобы найти оптимальное количество кластеров

def main():
    """
    Основная функция для загрузки данных, кластеризации, уменьшения размерности и визуализации.
    """
    print(f"--- Начало работы ---")

    # --- 1. Загрузка данных ---
    try:
        print(f"Загрузка данных из {INPUT_FILE}...")
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not data:
            print("Ошибка: Файл с эмбеддингами пуст.")
            return

        df = pd.DataFrame(data)
        print(f"Загружено {len(df)} записей.")
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути {INPUT_FILE}")
        print("Пожалуйста, сначала выполните экспорт эмбеддингов из Milvus.")
        return
    except json.JSONDecodeError:
        print(f"Ошибка: Не удалось прочитать JSON из файла {INPUT_FILE}.")
        return

    # Извлечение векторов в numpy массив
    vectors = np.array(df['vector'].tolist())

    # --- 2. Кластеризация K-Means ---
    print(f"Кластеризация данных на {N_CLUSTERS} кластеров с помощью K-Means...")
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init='auto')
    df['cluster'] = kmeans.fit_predict(vectors)
    print("Кластеризация завершена.")

    # --- 3. Уменьшение размерности UMAP ---
    print("Уменьшение размерности векторов до 2D с помощью UMAP...")
    reducer = umap.UMAP(n_components=2, random_state=42, n_jobs=1)
    embedding_2d = reducer.fit_transform(vectors)
    df[['x', 'y']] = embedding_2d
    print("Уменьшение размерности завершено.")

    # --- 4. Интерактивная визуализация Plotly ---
    print("Создание интерактивной визуализации...")

    # Обрезаем текст для более удобного отображения при наведении
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

    fig.update_traces(
        marker=dict(size=8, opacity=0.8),
        selector=dict(mode='markers')
    )

    fig.update_layout(
        legend_title_text='Кластеры',
        xaxis_title="UMAP 1",
        yaxis_title="UMAP 2",
    )

    # --- 5. Сохранение результата ---
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    fig.write_html(OUTPUT_FILE)
    print(f"✅ Визуализация успешно сохранена в файл: {os.path.abspath(OUTPUT_FILE)}")
    print("--- Работа завершена ---")


if __name__ == '__main__':
    main()
