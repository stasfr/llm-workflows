from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection
import psycopg
from psycopg import sql

from typing import List

from openai import OpenAI
import torch

MILVUS_ADDRESS = "http://192.168.1.101:19540"

# Milvus settings
COLLECTION_NAME = "photo_jeldor_cosine_flat_qwen_embedder"
VECTOR_DIMENSION = 4096

# PostgreSQL settings
POSTGRES_CONN_STRING = "dbname='dbname' user='user' host='192.168.1.101' port='5442' password='password'"
DB_TABLE_NAME = 'image_descriptions'

BATCH_SIZE = 128

class OpenAIEmbedder:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = OpenAI(
            base_url="http://192.168.1.101:1234/v1",
            api_key="not-needed" # required even if not used by the server
        )

    def get_embedding(self, text: List[str]) -> torch.Tensor:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text
        )

        embeddings = [item.embedding for item in response.data]

        # The OpenAI API /v1/embeddings endpoint returns normalized embeddings by default.
        return torch.tensor(embeddings)

    def get_query_embedding(self, text: str) -> torch.Tensor:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=[text]
        )

        embedding = response.data[0].embedding
        return torch.tensor(embedding).unsqueeze(0) # Return as a 2D tensor [1, dim]


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
        text_embedder = OpenAIEmbedder(model_name="text-embedding-qwen3-embedding-8b")

        with db_con.cursor() as cur:
            # Select all records from the database
            cur.execute(
                sql.SQL("SELECT post_id, text, photo_description FROM {}").format(sql.Identifier(DB_TABLE_NAME))
            )

            processed_count = 0

            while True:
                # Fetch records in batches
                records = cur.fetchmany(BATCH_SIZE)
                if not records:
                    break

                batch = []
                for record in records:
                    post_id, text, photo_description = record

                    # Handle potential None values
                    text = text or ""
                    photo_description = photo_description or ""

                    # Skip if both fields are empty
                    if not text and not photo_description:
                        continue

                    full_text = (text + " " + photo_description).strip()
                    batch.append({
                        "id": post_id,
                        "original_text": text,
                        "full_text": full_text,
                    })

                # Process the batch if it's not empty
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

                    processed_count += len(batch)
                    print(f"Processed {processed_count} records...")

        collection.flush()
        print(f"Total entities in collection: {collection.num_entities}")
    finally:
        db_con.close()

if __name__ == "__main__":
    main()
