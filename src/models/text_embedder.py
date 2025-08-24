from sentence_transformers import SentenceTransformer
import torch
from typing import List

class TextEmbedder:
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)

    def get_embedding(self, text: List[str]) -> torch.Tensor:
        embedding_tensor = self.model.encode(
            text,
            normalize_embeddings=True,
            convert_to_tensor=True
        )
        return embedding_tensor

    def get_query_embedding(self, text: str, instruction: str = "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery: ") -> torch.Tensor:
        input_text = f"{instruction}{text}" if instruction else text

        embedding_tensor = self.model.encode(
            input_text,
            normalize_embeddings=True,
            convert_to_tensor=True
        )
        return embedding_tensor
