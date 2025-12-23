from typing import List, Optional, Any
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, SecretStr, Field
import openai
import os

class SiliconFlowEmbeddings(BaseModel, Embeddings):
    """SiliconFlow embedding models."""

    client: Any = None
    model: str = "BAAI/bge-m3"
    api_key: Optional[str] = None
    base_url: str = "https://api.siliconflow.cn/v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.api_key:
            self.api_key = os.getenv("SILICONFLOW_API_KEY")
        
        if not self.api_key:
            raise ValueError("SiliconFlow API key not found. Please set SILICONFLOW_API_KEY environment variable or pass it to the constructor.")

        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        texts = [t.replace("\n", " ") for t in texts]
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            print(f"Error embedding documents: {e}")
            return []

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        text = text.replace("\n", " ")
        try:
            response = self.client.embeddings.create(
                input=[text],
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error embedding query: {e}")
            # Return a zero vector or raise, depending on needs. 
            # Returning empty list might cause downstream issues in Chroma.
            # Let's raise to be safe and see the error.
            raise e
            print(f"Error embedding query: {e}")
            return []
