import json
import asyncio
import time
from pathlib import Path
import chromadb
from chromadb.config import Settings
from config import settings


class EmbeddingService:
    def __init__(self):
        self.catalog_path = Path(__file__).parent.parent / "data" / "catalog.json"
        self.catalog = self._load_catalog()
        self.client = None
        self.collection = None
        self._initialized = False
        # Attempt connection; if it fails, we fall back to keyword search
        self._try_init_chroma(retries=5, delay=3)

    def _load_catalog(self):
        try:
            with open(self.catalog_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[EmbeddingService] catalog.json not found, using empty catalog: {e}")
            return {}

    def _try_init_chroma(self, retries: int = 5, delay: float = 3.0):
        for attempt in range(1, retries + 1):
            try:
                self.client = chromadb.HttpClient(
                    host=settings.CHROMA_HOST,
                    port=int(settings.CHROMA_PORT),
                    settings=Settings(allow_reset=True),
                )
                # Confirm server is alive
                self.client.heartbeat()
                self._init_collection()
                self._initialized = True
                print(f"[EmbeddingService] ChromaDB connected on attempt {attempt}")
                return
            except Exception as e:
                print(f"[EmbeddingService] ChromaDB attempt {attempt}/{retries} failed: {e}")
                if attempt < retries:
                    time.sleep(delay)

        print("[EmbeddingService] ChromaDB unavailable — falling back to keyword search")

    def _init_collection(self):
        """Create or reuse the catalog collection. Uses simple text embedding (no Google API needed for indexing)."""
        try:
            self.collection = self.client.get_or_create_collection(name="sap_catalog")

            if self.collection.count() == 0 and self.catalog:
                documents = []
                metadatas = []
                ids = []
                for key, value in self.catalog.items():
                    ids.append(key)
                    documents.append(
                        f"{key}: {value.get('business_name', key)} - {value.get('description', '')}"
                    )
                    metadatas.append({"key": key})

                batch_size = 100
                for i in range(0, len(ids), batch_size):
                    self.collection.add(
                        ids=ids[i : i + batch_size],
                        documents=documents[i : i + batch_size],
                        metadatas=metadatas[i : i + batch_size],
                    )
                print(f"[EmbeddingService] Indexed {len(ids)} catalog entries in ChromaDB.")
            else:
                print(
                    f"[EmbeddingService] Collection already has {self.collection.count()} entries."
                )
        except Exception as e:
            print(f"[EmbeddingService] Collection init failed: {e}")
            self.collection = None

    async def retrieve_schema_context(self, query: str, top_k: int = 8) -> str:
        if self.collection:
            try:
                results = await asyncio.to_thread(
                    self.collection.query,
                    query_texts=[query],
                    n_results=min(top_k, max(1, self.collection.count())),
                )
                if results and results["documents"] and results["documents"][0]:
                    return "\n".join(results["documents"][0])
            except Exception as e:
                print(f"[EmbeddingService] ChromaDB query failed: {e}")

        # Fallback: keyword match against in-memory catalog
        query_words = set(query.lower().split())
        scored = []
        for key, value in self.catalog.items():
            text = f"{key} {value.get('business_name', '')} {value.get('description', '')}".lower()
            score = sum(1 for w in query_words if w in text)
            if score > 0:
                scored.append(
                    (
                        score,
                        f"{key}: {value.get('business_name', key)} - {value.get('description', '')}",
                    )
                )
        scored.sort(reverse=True, key=lambda x: x[0])
        return "\n".join(doc for _, doc in scored[:top_k])


# Module-level singleton
_instance: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    global _instance
    if _instance is None:
        _instance = EmbeddingService()
    return _instance


class _LazyProxy:
    """Backward-compat proxy so `from services.embedding_service import embedding_service` still works."""

    def __getattr__(self, name):
        return getattr(get_embedding_service(), name)


embedding_service = _LazyProxy()
