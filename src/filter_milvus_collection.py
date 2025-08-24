from pymilvus import connections, utility, Collection, FieldSchema, DataType, CollectionSchema
from tqdm import tqdm
import consts

# Milvus settings
MILVUS_ADDRESS = "http://localhost:19530"
CURRENT_COLLECTION_NAME = "filtered_jeldor_cosine_flat"
NEW_COLLECTION_NAME = "filtered_it_5_jeldor_cosine_flat"
VECTOR_DIMENSION = 1024  # For intfloat/multilingual-e5-large-instruct
BATCH_SIZE = 128

def create_milvus_collection(collection_name: str, vector_dim: int):
    """
    Creates a new Milvus collection with a predefined schema.
    """
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=vector_dim),
        FieldSchema(name="post_id", dtype=DataType.INT64),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
    ]
    schema = CollectionSchema(fields, description="Filtered Telegram data")
    collection = Collection(name=collection_name, schema=schema, using='default')

    index_params = {
        "metric_type": "COSINE",
        "index_type": "FLAT",
        "params": {}
    }
    collection.create_index(field_name="vector", index_params=index_params, index_name="vector_idx")
    print(f"Collection '{collection_name}' created with index.")
    return collection

def main():
    """
    Main function to filter a Milvus collection.
    """
    connections.connect("default", uri=MILVUS_ADDRESS)

    # Convert GARBAGE_IDS to a set for efficient lookup
    garbage_ids_set = set(consts.GARBAGE_IDS)
    print(f"Converted {len(garbage_ids_set)} garbage IDs to a set for efficient filtering.")

    if utility.has_collection(NEW_COLLECTION_NAME):
        print(f"Collection '{NEW_COLLECTION_NAME}' already exists. Halting execution to prevent data loss.")
        return

    print(f"Creating new collection: '{NEW_COLLECTION_NAME}'")
    new_collection = create_milvus_collection(NEW_COLLECTION_NAME, VECTOR_DIMENSION)

    if not utility.has_collection(CURRENT_COLLECTION_NAME):
        print(f"Current collection '{CURRENT_COLLECTION_NAME}' not found. Nothing to filter.")
        return

    current_collection = Collection(CURRENT_COLLECTION_NAME)
    current_collection.load()
    print(f"Loaded collection '{CURRENT_COLLECTION_NAME}'.")

    total_entities = current_collection.num_entities
    print(f"Total entities to process: {total_entities}")

    with tqdm(total=total_entities, desc="Filtering and inserting data") as pbar:
        for offset in range(0, total_entities, BATCH_SIZE):
            batch = current_collection.query(
                expr="post_id > 0",
                output_fields=["post_id", "text", "vector"],
                limit=BATCH_SIZE,
                offset=offset
            )

            data_to_insert = []
            for entity in batch:
                if entity['post_id'] not in garbage_ids_set:  # Use the set here for speed
                    data_to_insert.append({
                        "post_id": entity['post_id'],
                        "text": entity['text'],
                        "vector": entity['vector']
                    })

            if data_to_insert:
                new_collection.insert(data_to_insert)

            pbar.update(len(batch))

    new_collection.flush()

    print("\nFiltering complete.")
    print(f"Total entities in old collection ('{CURRENT_COLLECTION_NAME}'): {current_collection.num_entities}")
    print(f"Total entities in new collection ('{NEW_COLLECTION_NAME}'): {new_collection.num_entities}")


if __name__ == "__main__":
    main()
