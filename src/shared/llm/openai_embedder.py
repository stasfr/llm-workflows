from src.config import LLM_API_URL

from typing import List

from openai import OpenAI
import torch


class OpenAIEmbedder:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = OpenAI(
            base_url=LLM_API_URL,
            api_key="not-needed"  # required even if not used by the server
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
        # Return as a 2D tensor [1, dim]
        return torch.tensor(embedding).unsqueeze(0)
