from src.modules.db_milvus.repository import MilvusRepository

def get_collection_list() -> list[str]:
    return MilvusRepository.get_all_collections()

def create_new_collection(collection_name: str, dim: int) -> None:
    if not collection_name:
        raise ValueError("Collection name is required")
    if MilvusRepository.has_collection(collection_name):
        raise ValueError(f"Collection '{collection_name}' already exists.")

    MilvusRepository.create_collection(collection_name, dim)

def delete_collection(collection_name: str) -> None:
    if not collection_name:
        raise ValueError("Collection name is required")
    if not MilvusRepository.has_collection(collection_name):
        raise ValueError(f"Collection '{collection_name}' does not exist.")

    MilvusRepository.delete_collection(collection_name)
