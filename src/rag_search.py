import models
from pymilvus import connections, Collection

# Milvus settings from embeddings.py
MILVUS_ADDRESS = "http://localhost:19530"
COLLECTION_NAME = "filtered_jeldor_cosine_flat"

def search_similar_texts(query: str, collection: Collection, embedder, top_k: int = 5):
    """
    Embeds a query string and searches for similar texts in the Milvus collection.

    Args:
        query (str): The input text to search for.
        collection (Collection): The Milvus collection object.
        embedder: The text embedder model instance.
        top_k (int): The number of similar results to return.

    Returns:
        list: A list of search results.
    """
    print(f"Searching for: '{query}'")

    # 1. Generate embedding for the query
    query_embedding = embedder.get_embedding([query]).tolist()

    # 2. Define search parameters
    # For FLAT index, params can be empty.
    search_params = {
        "metric_type": "COSINE",
        "params": {},
    }

    # 3. Perform the search
    results = collection.search(
        data=query_embedding,
        anns_field="vector",
        param=search_params,
        limit=top_k,
        output_fields=["text", "post_id"]
    )

    # 4. Process and return results
    processed_results = []
    print("\n--- Search Results ---")
    if not results:
        print("Search returned no results.")
        return processed_results

    # results is a list of hit-lists, one for each query vector.
    # We iterate through the results for our single query.
    for hits in results: # type: ignore
        if not hits:
            print("Query returned no hits.")
            continue
        for hit in hits:
            result_item = {
                "id": hit.id,
                "distance": hit.distance,
                "post_id": hit.entity.get('post_id'),
                "text": hit.entity.get('text')
            }
            processed_results.append(result_item)
            print(f"Distance: {hit.distance:.4f}, Post ID: {result_item['post_id']}\nText: {result_item['text']}\n---")

    return processed_results

def main():
    """
    Main function to connect to Milvus, run a search, and print results.
    """
    # 1. Connect to Milvus
    print(f"Connecting to Milvus at {MILVUS_ADDRESS}...")
    connections.connect("default", uri=MILVUS_ADDRESS)

    # 2. Get collection and load it
    print(f"Loading collection '{COLLECTION_NAME}'...")
    collection = Collection(COLLECTION_NAME)
    collection.load()
    print(f"Collection loaded. Total entities: {collection.num_entities}")


    # 3. Initialize embedder
    print("Loading text embedder model...")
    text_embedder = models.OpenAIEmbedder(model_name="intfloat/multilingual-e5-large-instruct")
    print("Model loaded.")

    # 4. Example Query
    query_text = "собака"


    # 5. Run search
    search_similar_texts(query_text, collection, text_embedder, top_k=15)

    # Disconnect from Milvus
    connections.disconnect("default")

if __name__ == "__main__":
    main()
