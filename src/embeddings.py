import os
import models
from tqdm import tqdm
from process_tg_data import count_json_items, stream_filtered_tg_data
from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection

WORKING_DIR = './output'
FILTERED_FILE = os.path.join(WORKING_DIR, 'filtered_telegram_data.json')

# Milvus settings
MILVUS_ADDRESS = "http://localhost:19530"
COLLECTION_NAME = "test_cosine_flat" # DataName_MetricType_IndexType
VECTOR_DIMENSION = 1024 # For intfloat/multilingual-e5-large-instruct

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

    if not utility.has_collection(COLLECTION_NAME):
        print(f"Collection '{COLLECTION_NAME}' does not exist. Creating...")
        create_milvus_collection(COLLECTION_NAME, VECTOR_DIMENSION)
        print(f"Collection '{COLLECTION_NAME}' created.")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")

    collection = Collection(COLLECTION_NAME)
    collection.load()

    print('Loading models')
    # image_describer = models.ImageDescription(model_name="google/gemma-3-4b-it")
    text_embedder = models.OpenAIEmbedder(model_name="intfloat/multilingual-e5-large-instruct")

    total_items = count_json_items(FILTERED_FILE, 'item')
    filtered_tg_data = stream_filtered_tg_data(FILTERED_FILE)

    batch_size = 32
    batch = []

    with tqdm(total=total_items, desc="Processing parsed posts") as pbar:
        for item in filtered_tg_data:
            if 'text' in item and item['text'].strip():
                batch.append(item)

            if len(batch) >= batch_size:
                texts_to_embed = [item['text'] for item in batch]
                embeddings = text_embedder.get_embedding(
                    texts_to_embed
                ).tolist()

                data_to_insert = [
                    {"post_id": item['id'], "text": item['text'], "vector": emb}
                    for item, emb in zip(batch, embeddings)
                ]
                collection.insert(data_to_insert)
                batch = []

            pbar.update(1)

    if batch:
        texts_to_embed = [item['text'] for item in batch]
        embeddings = text_embedder.get_embedding(
            texts_to_embed
        ).tolist()

        data_to_insert = [
            {"post_id": item['id'], "text": item['text'], "vector": emb}
            for item, emb in zip(batch, embeddings)
        ]
        collection.insert(data_to_insert)

    collection.flush()
    print(f"Total entities in collection: {collection.num_entities}")

if __name__ == "__main__":
    main()
