from fastembed import TextEmbedding
from backend.config import EMBED_MODEL

class Embedder:
    def __init__(self):
        self.model = TextEmbedding(model_name=EMBED_MODEL)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return list(self.model.embed(texts))

    def embed_query(self, query: str) -> list[float]:
        return list(self.model.embed([query]))[0]
