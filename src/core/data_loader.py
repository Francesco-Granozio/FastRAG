from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from src.providers.embedding_providers import get_embedding_provider

# ============================================================================
# CONSTANTS - Text chunking settings
# ============================================================================
DEFAULT_CHUNK_SIZE = 1000  # Dimensione massima di ogni chunk di testo (caratteri)
DEFAULT_CHUNK_OVERLAP = 200  # Numero di caratteri di overlap tra chunk consecutivi

splitter = SentenceSplitter(chunk_size=DEFAULT_CHUNK_SIZE, chunk_overlap=DEFAULT_CHUNK_OVERLAP)

# Get the embedding provider instance
_embedding_provider = None


def _get_embedding_provider():
    """Lazy initialization of embedding provider."""
    global _embedding_provider
    if _embedding_provider is None:
        _embedding_provider = get_embedding_provider()
    return _embedding_provider


def load_and_chunk_pdf(path: str):
    docs = PDFReader().load_data(file=path)
    texts = [d.text for d in docs if getattr(d, "text", None)]
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))
    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using the configured provider."""
    provider = _get_embedding_provider()
    return provider.embed(texts)


def get_embedding_dimension() -> int:
    """Get the embedding dimension for the current provider."""
    provider = _get_embedding_provider()
    return provider.get_dimension()
