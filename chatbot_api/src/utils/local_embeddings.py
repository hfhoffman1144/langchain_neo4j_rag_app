import os
from typing import List

_MODEL_NAME = os.getenv("LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")


class LocalEmbeddings:
    """Lightweight local embedding wrapper using sentence-transformers.

    Provides `embed_documents` and `embed_query` methods similar to
    `OpenAIEmbeddings` used in this repo. The model is loaded lazily.
    """

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or _MODEL_NAME
        self._model = None

    def _load(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except Exception as e:
                raise RuntimeError("sentence-transformers is required for LocalEmbeddings: pip install sentence-transformers") from e
            self._model = SentenceTransformer(self.model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        self._load()
        embs = self._model.encode(texts, convert_to_numpy=True)
        # convert to Python lists for JSON persistence
        return [emb.tolist() for emb in embs]

    def embed_query(self, text: str) -> List[float]:
        self._load()
        emb = self._model.encode(text, convert_to_numpy=True)
        return emb.tolist()
