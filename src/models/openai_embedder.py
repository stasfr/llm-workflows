from openai import OpenAI
import torch
from typing import List

class OpenAIEmbedder:
    def __init__(self, model_name: str, api_base: str = "http://127.0.0.1:1234/v1"):
        self.model_name = model_name
        self.client = OpenAI(
            base_url=api_base,
            api_key="dummy" # required even if not used by the server
        )

    def get_embedding(self, text: List[str]) -> torch.Tensor:
        """
        Gets embeddings for a list of texts from an OpenAI-compatible API.
        """
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text
        )
        
        embeddings = [item.embedding for item in response.data]
        
        # The OpenAI API /v1/embeddings endpoint returns normalized embeddings by default.
        return torch.tensor(embeddings)

    def get_query_embedding(self, text: str) -> torch.Tensor:
        """
        Gets an embedding for a single query text.
        """
        response = self.client.embeddings.create(
            model=self.model_name,
            input=[text]
        )
        
        embedding = response.data[0].embedding
        return torch.tensor(embedding).unsqueeze(0) # Return as a 2D tensor [1, dim]
