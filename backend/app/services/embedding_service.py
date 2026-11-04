
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_query(self, text: str):
        embedding = self.model.encode(
            text,
            convert_to_numpy=True
        )

        return embedding

    def embed_documents(self, texts: list[str]):
        return self.model.encode(
            texts,
            convert_to_numpy=True
        )