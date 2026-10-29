
import os
from pathlib import Path

import chromadb
from backend.embedder import Embedder


class Retriever:
    """Semantic retrieval using persistent ChromaDB."""

    def __init__(self):
        self.embedder = Embedder()
        persist_dir = Path(
            os.getenv("CHROMA_PATH", "./chroma_store")
        ).resolve()
        persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(
            name="legal_documents",
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: list[dict]) -> None:
        ids, documents, metadatas = [], [], []

        for index, chunk in enumerate(chunks):
            text = chunk.get("text", "").strip()
            if not text:
                continue

            metadata = chunk.get("metadata", {})
            source = str(metadata.get("source", "unknown"))
            chunk_id = metadata.get("chunk_id", index)

            ids.append(str(chunk.get("id") or f"{source}_chunk_{chunk_id}"))
            documents.append(text)

            clean_metadata = {
                str(key): value
                for key, value in metadata.items()
                if isinstance(value, (str, int, float, bool))
            }
            clean_metadata["source"] = source
            clean_metadata["chunk_id"] = int(chunk_id)
            metadatas.append(clean_metadata)

        if not documents:
            return

        embeddings = [
            vector.tolist() if hasattr(vector, "tolist") else list(vector)
            for vector in self.embedder.embed(documents)
        ]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def query(self, query: str, top_k: int = 5) -> list[dict]:
        query = query.strip()
        if not query or top_k < 1:
            return []

        total = self.collection.count()
        if total == 0:
            return []

        query_vector = self.embedder.embed_query(query)
        if hasattr(query_vector, "tolist"):
            query_vector = query_vector.tolist()

        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, total),
            include=["documents", "metadatas", "distances"],
        )

        retrieved = []
        for text, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            metadata = metadata or {}
            distance = float(distance)

            retrieved.append({
                "text": text,
                "source": metadata.get("source", "unknown"),
                "legal_address": metadata.get(
                    "legal_address",
                    metadata.get("source", "unknown"),
                ),
                "score": round(1.0 / (1.0 + max(distance, 0.0)), 4),
                "distance": round(distance, 4),
            })

        return retrieved

    def count(self) -> int:
        return self.collection.count()
