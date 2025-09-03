import os
import models
from tqdm import tqdm
from process_tg_data import count_json_items, stream_filtered_tg_data
from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection
import psycopg
from psycopg import sql

WORKING_DIR = './output'
FILTERED_FILE = os.path.join(WORKING_DIR, 'filtered_telegram_data.json')

# Milvus settings
MILVUS_ADDRESS = "http://localhost:19530"
COLLECTION_NAME = "photo_jeldor_cosine_flat" # DataName_MetricType_IndexType
VECTOR_DIMENSION = 1024 # For intfloat/multilingual-e5-large-instruct

# PostgreSQL settings
POSTGRES_CONN_STRING = "dbname='dbname' user='user' host='localhost' port='5442' password='password'"
DB_TABLE_NAME = 'image_descriptions'

BATCH_SIZE = 128

def create_milvus_collection(collection_name: str, vector_dim: int):
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


def main():
    connections.connect("default", uri=MILVUS_ADDRESS)

    try:
        db_con = psycopg.connect(POSTGRES_CONN_STRING)
    except psycopg.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
        print("Please ensure PostgreSQL is running and the connection string is correct.")
        return

    try:
        if not utility.has_collection(COLLECTION_NAME):
            print(f"Collection '{COLLECTION_NAME}' does not exist. Creating...")
            create_milvus_collection(COLLECTION_NAME, VECTOR_DIMENSION)
            print(f"Collection '{COLLECTION_NAME}' created.")
        else:
            print(f"Collection '{COLLECTION_NAME}' already exists.")

        collection = Collection(COLLECTION_NAME)
        collection.load()

        print('Loading models')
        text_embedder = models.OpenAIEmbedder(model_name="intfloat/multilingual-e5-large-instruct")

        total_items = count_json_items(FILTERED_FILE, 'item')
        filtered_tg_data = stream_filtered_tg_data(FILTERED_FILE)

        batch = []

        with tqdm(total=total_items, desc="Processing parsed posts") as pbar, db_con.cursor() as cur:
            for item in filtered_tg_data:
                post_id = item.get('id')
                if not post_id:
                    pbar.update(1)
                    continue

                cur.execute(
                    sql.SQL("SELECT photo_description FROM {} WHERE post_id = %s").format(sql.Identifier(DB_TABLE_NAME)),
                    (post_id,)
                )
                photo_desc_res = cur.fetchone()

                photo_description = photo_desc_res[0] if photo_desc_res and photo_desc_res[0] else ""
                item_text = item.get('text', "").strip()

                if not item_text and not photo_description:
                    pbar.update(1)
                    continue

                full_text = (item_text + " " + photo_description).strip()
                batch.append({
                    "id": post_id,
                    "original_text": item_text,
                    "full_text": full_text,
                })

                if len(batch) >= BATCH_SIZE:
                    texts_to_embed = [b_item['full_text'] for b_item in batch]
                    embeddings = text_embedder.get_embedding(
                        texts_to_embed
                    ).tolist()

                    data_to_insert = [
                        {"post_id": b_item['id'], "text": b_item['original_text'], "vector": emb}
                        for b_item, emb in zip(batch, embeddings)
                    ]
                    collection.insert(data_to_insert)
                    batch = []

                pbar.update(1)

        if batch:
            texts_to_embed = [b_item['full_text'] for b_item in batch]
            embeddings = text_embedder.get_embedding(
                texts_to_embed
            ).tolist()

            data_to_insert = [
                {"post_id": b_item['id'], "text": b_item['original_text'], "vector": emb}
                for b_item, emb in zip(batch, embeddings)
            ]
            collection.insert(data_to_insert)

        collection.flush()
        print(f"Total entities in collection: {collection.num_entities}")
    finally:
        db_con.close()

if __name__ == "__main__":
    main()
