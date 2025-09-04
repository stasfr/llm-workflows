import os
import json
import ijson
from typing import Generator, Optional, Callable

from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection
import psycopg
from psycopg import sql

from config import (
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT,
    MILVUS_HOST, MILVUS_PORT, STORAGE_FOLDER
)

from llm.openai_embedder import OpenAIEmbedder
from utils.count_json_items import count_json_items


def stream_filtered_tg_data(filename: str) -> Generator[dict, None, None]:
    """
    Генератор для потоковой передачи данных из файла JSON, содержащего список элементов.
    Yields словари из списка верхнего уровня.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            # Отфильтрованный файл представляет собой плоский список объектов
            yield from ijson.items(f, 'item')
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути {filename}")
        raise
    except json.JSONDecodeError:
        print(f"Ошибка: Не удалось прочитать JSON из файла {filename}.")
        raise


def create_milvus_collection(collection_name: str, vector_dim: int):
    """Создает новую коллекцию Milvus с указанной схемой."""
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=vector_dim),
        FieldSchema(name="post_id", dtype=DataType.INT64),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
    ]
    schema = CollectionSchema(fields)
    collection = Collection(name=collection_name, schema=schema, using='default')

    index_params = {
        "metric_type": "COSINE",
        "index_type": "FLAT",
        "params": {}
    }
    collection.create_index(field_name="vector", index_params=index_params, index_name="vector_idx")


def create_embeddings(
    db_name: str,
    project_name: str,
    project_snapshot: str,
    collection_name: str,
    db_table_name: str,
    model_name: str,
    vector_dimension: int,
    batch_size: int = 128,
    progress_callback: Optional[Callable[[int, int], None]] = None,
):
    """
    Создает эмбеддинги для текстовых данных и сохраняет их в коллекции Milvus.

    Args:
        project_name (str): Название проекта.
        project_snapshot (str): Снимок/версия проекта.
        collection_name (str): Название коллекции Milvus.
        db_table_name (str): Название таблицы PostgreSQL для описаний изображений.
        model_name (str): Название модели для создания эмбеддингов.
        vector_dimension (int): Размерность векторов.
        batch_size (int, optional): Размер пакета для обработки. По умолчанию 128.
        progress_callback (Optional[Callable[[int, int], None]], optional):
            Обратный вызов для отслеживания прогресса. По умолчанию None.
    """
    # --- 1. Настройка соединений и путей ---
    MILVUS_ADDRESS = f"http://{MILVUS_HOST}:{MILVUS_PORT}"
    POSTGRES_CONN_STRING = f"dbname='{db_name}' user='{DB_USER}' host='{DB_HOST}' port='{DB_PORT}' password='{DB_PASSWORD}'"
    PROJECT_DIR = os.path.join(STORAGE_FOLDER, 'projects', f"{project_name}_{project_snapshot}")
    FILTERED_FILE = os.path.join(PROJECT_DIR, 'filtered_telegram_data.json')

    connections.connect("default", uri=MILVUS_ADDRESS)

    try:
        db_con = psycopg.connect(POSTGRES_CONN_STRING)
    except psycopg.OperationalError as e:
        print(f"Ошибка подключения к PostgreSQL: {e}")
        raise

    try:
        # --- 2. Настройка коллекции Milvus ---
        if not utility.has_collection(collection_name):
            create_milvus_collection(collection_name, vector_dimension)

        collection = Collection(collection_name)
        collection.load()

        # --- 3. Инициализация моделей и потока данных ---
        text_embedder = OpenAIEmbedder(model_name=model_name)

        total_items = count_json_items(FILTERED_FILE, 'item')
        if total_items == 0:
            print("Нет элементов для обработки.")
            return

        filtered_tg_data = stream_filtered_tg_data(FILTERED_FILE)
        batch = []
        processed_count = 0

        # --- 4. Обработка данных пакетами ---
        with db_con.cursor() as cur:
            for item in filtered_tg_data:
                post_id = item.get('id')
                if not post_id:
                    processed_count += 1
                    if progress_callback:
                        progress_callback(processed_count, total_items)
                    continue

                # Получение соответствующего описания фото из PostgreSQL
                cur.execute(
                    sql.SQL("SELECT photo_description FROM {} WHERE post_id = %s").format(sql.Identifier(db_table_name)),
                    (post_id,)
                )
                photo_desc_res = cur.fetchone()

                photo_description = photo_desc_res[0] if photo_desc_res and photo_desc_res[0] else ""
                item_text = item.get('text', "").strip()

                # Пропускаем, если нет текстового содержимого
                if not item_text and not photo_description:
                    processed_count += 1
                    if progress_callback:
                        progress_callback(processed_count, total_items)
                    continue

                full_text = (item_text + " " + photo_description).strip()
                batch.append({
                    "id": post_id,
                    "original_text": item_text,
                    "full_text": full_text,
                })

                # Обрабатываем пакет при его заполнении
                if len(batch) >= batch_size:
                    texts_to_embed = [b_item['full_text'] for b_item in batch]
                    embeddings = text_embedder.get_embedding(texts_to_embed).tolist()

                    data_to_insert = [
                        {"post_id": b_item['id'], "text": b_item['original_text'], "vector": emb}
                        for b_item, emb in zip(batch, embeddings)
                    ]
                    collection.insert(data_to_insert)
                    batch = []

                processed_count += 1
                if progress_callback:
                    progress_callback(processed_count, total_items)

        # --- 5. Обработка оставшихся элементов в последнем пакете ---
        if batch:
            texts_to_embed = [b_item['full_text'] for b_item in batch]
            embeddings = text_embedder.get_embedding(texts_to_embed).tolist()

            data_to_insert = [
                {"post_id": b_item['id'], "text": b_item['original_text'], "vector": emb}
                for b_item, emb in zip(batch, embeddings)
            ]
            collection.insert(data_to_insert)

        # --- 6. Завершение и отчет ---
        collection.flush()

    finally:
        db_con.close()
        connections.disconnect("default")
