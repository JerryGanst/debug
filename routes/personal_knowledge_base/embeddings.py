from __future__ import annotations
from typing import List
import httpx
from langchain_core.embeddings import Embeddings

from configs.load import load_config,ModelRouter

config = load_config()
model_router = ModelRouter(config)

embedding_batch_api_url = model_router.get_embedding_batch_api_url()

class RemoteBGEEmbeddings(Embeddings):
    """调用本地 /embed_batch/ 的自定义 Embeddings"""
    def __init__(self, api_url: str = embedding_batch_api_url):
        self.api_url = api_url
        self.client = httpx.Client(timeout=30)

    def _batch_call(self, texts: List[str]) -> List[List[float]]:
        r = self.client.post(self.api_url, json={"texts": texts})
        r.raise_for_status()
        return r.json()["embeddings"]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._batch_call(texts) if texts else []

    def embed_query(self, text: str) -> List[float]:
        return self._batch_call([text])[0]