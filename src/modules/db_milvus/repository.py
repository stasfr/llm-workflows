from pymilvus import (
    db,
    connections,
    utility,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
)
from src.config import MILVUS_HOST, MILVUS_PORT

class MilvusRepository:
    @staticmethod
    def _connect():
        if "milvus_ops" not in connections.list_connections():
            connections.connect(alias="milvus_ops", host=MILVUS_HOST, port=MILVUS_PORT)
        # Ensure we are using the default database
        db.using_database("default", using="milvus_ops")

    @staticmethod
    def _disconnect():
        if "milvus_ops" in connections.list_connections():
            connections.disconnect(alias="milvus_ops")

    @classmethod
    def get_all_collections(cls) -> list[str]:
        cls._connect()
        try:
            collections = utility.list_collections(using="milvus_ops")
        finally:
            cls._disconnect()
        return collections

    @classmethod
    def create_collection(cls, collection_name: str, dim: int) -> None:
        cls._connect()
        try:
            # Define a default schema
            fields = [
                FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="psql_id", dtype=DataType.VARCHAR, max_length=64,
                            description="UUID of the corresponding entry in PostgreSQL"),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim)
            ]
            schema = CollectionSchema(
                fields,
                description=f"Collection {collection_name}"
            )
            Collection(
                name=collection_name,
                schema=schema,
                using="milvus_ops"
            )
        finally:
            cls._disconnect()

    @classmethod
    def delete_collection(cls, collection_name: str) -> None:
        cls._connect()
        try:
            utility.drop_collection(collection_name=collection_name, using="milvus_ops")
        finally:
            cls._disconnect()

    @classmethod
    def has_collection(cls, collection_name: str) -> bool:
        cls._connect()
        try:
            result = utility.has_collection(collection_name=collection_name, using="milvus_ops")
        finally:
            cls._disconnect()
        return result
