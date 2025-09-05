from pymilvus import connections, Collection
from typing import List, Dict, Any

from config import MILVUS_ADDRESS
import llm


def search_similar_items(
    query: str,
    collection_name: str,
    model_name: str,
    top_k: int,
    output_fields: List[str],
) -> List[Dict[str, Any]]:
    """
    Embeds a query and searches for similar items in a Milvus collection.
    This function is designed to be used as an event handler in a FastAPI application.

    Args:
        query (str): The input text to search for.
        collection_name (str): The name of the Milvus collection.
        model_name (str): The name of the sentence transformer model to use for embedding.
        top_k (int): The number of similar results to return.
        output_fields (List[str]): The fields to retrieve from the collection.

    Returns:
        List[Dict[str, Any]]: A list of search results, each containing distance and output fields.
    """
    processed_results = []

    try:
        connections.connect("default", uri=MILVUS_ADDRESS)

        collection = Collection(collection_name)
        collection.load()

        embedder = llm.OpenAIEmbedder(model_name=model_name)
        query_embedding = embedder.get_embedding([query]).tolist()

        search_params = {
            "metric_type": "COSINE",
            "params": {},
        }

        results = collection.search(
            data=query_embedding,
            anns_field="vector",
            param=search_params,
            limit=top_k,
            output_fields=output_fields
        )

        if not results:
            print(f"Warning: Search in collection '{collection_name}' returned no results for query: '{query}'")
            return processed_results

        for hits in results:  # type: ignore
            if not hits:
                print(f"Warning: Query returned no hits in collection '{collection_name}'.")
                continue
            for hit in hits:
                result_item = {
                    "id": hit.id,
                    "distance": hit.distance,
                }
                for field in output_fields:
                    result_item[field] = hit.entity.get(field) if hit.entity else None
                processed_results.append(result_item)

        return processed_results

    except Exception as e:
        print(f"An error occurred during vector search: {e}")
        raise
    finally:
        if connections.has_connection("default"):
            connections.disconnect("default")
