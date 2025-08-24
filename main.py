import os
from tg_parsing.parser import parse_raw_telegram_data, filter_parsed_telegram_data
import models
from tqdm import tqdm
from tg_parsing.parser import count_json_items, stream_filtered_tg_data
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

    print('Parsing and filtering Telegram Data')
    parse_raw_telegram_data()
    filter_parsed_telegram_data([], [], [], 3)

    print('Loading models')
    image_describer = models.ImageDescription(model_name="google/gemma-3-4b-it")
    text_embedder = models.TextEmbedder(model_name="intfloat/multilingual-e5-large-instruct")

    total_items = count_json_items(FILTERED_FILE, 'item')
    filtered_tg_data = stream_filtered_tg_data(FILTERED_FILE)

    with tqdm(total=total_items, desc="Processing posts") as pbar:
        for item in filtered_tg_data:
            pbar.update(1)

if __name__ == "__main__":
    main()
