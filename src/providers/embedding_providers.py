"""Embedding provider implementations."""

from abc import ABC, abstractmethod
from typing import List
import requests
from openai import OpenAI
from src.core.config import ModelConfig

# ============================================================================
# CONSTANTS - API timeout settings
# ============================================================================
DEFAULT_EMBEDDING_TIMEOUT = 60  # Timeout per richieste embedding API (secondi)


class EmbeddingProvider(ABC):
    """Base class for embedding providers."""

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Get the dimension of embeddings produced by this provider."""
        pass


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Embedding provider using Ollama API."""

    def __init__(
        self,
        base_url: str = None,
        model: str = None,
    ):
        self.base_url = base_url or ModelConfig.OLLAMA_BASE_URL
        self.model = model or ModelConfig.OLLAMA_EMBEDDING_MODEL
        self.dimension = ModelConfig.get_embedding_dimension()

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Ollama API."""
        embeddings = []
        for text in texts:
            last_error = None
            # Prova prima con 'input', poi con 'prompt' se fallisce
            for field_name in ["input", "prompt"]:
                try:
                    response = requests.post(
                        f"{self.base_url}/api/embed",
                        json={"model": self.model, field_name: text},
                        timeout=DEFAULT_EMBEDDING_TIMEOUT,
                    )
                    response.raise_for_status()
                    result = response.json()
                    # Ollama restituisce 'embeddings' (plurale) come array di array
                    embedding_list = result.get("embeddings", [])
                    # Se non c'è 'embeddings', prova 'embedding' (singolare) per retrocompatibilità
                    if not embedding_list:
                        single_embedding = result.get("embedding", [])
                        if single_embedding:
                            embedding_list = [single_embedding]

                    if embedding_list and len(embedding_list) > 0:
                        # Prendi il primo embedding dall'array (è già un array di float)
                        embedding = embedding_list[0]
                        if embedding and len(embedding) > 0:
                            embeddings.append(embedding)
                            break
                    else:
                        # Risposta OK ma senza embedding
                        last_error = f"Risposta senza embedding dal server (campo '{field_name}')"
                        if field_name == "input":
                            # Abbiamo provato entrambi
                            raise ValueError(
                                f"Impossibile generare embedding. {last_error}\n"
                                f"Verifica che:\n"
                                f"1. Il modello '{self.model}' sia installato (esegui: ollama pull {self.model})\n"
                                f"2. Il modello supporti embeddings"
                            )
                        continue
                except requests.exceptions.HTTPError as e:
                    last_error = (
                        f"HTTP {e.response.status_code}: {e.response.text[:200]}"
                    )
                    if e.response.status_code == 404:
                        # Se 404, potrebbe essere che il modello non esista o endpoint sbagliato
                        if field_name == "input":
                            # Abbiamo provato entrambi, solleva l'errore
                            raise ValueError(
                                f"Errore 404: Verifica che:\n"
                                f"1. Ollama sia in esecuzione su {self.base_url}\n"
                                f"2. Il modello '{self.model}' sia installato (esegui: ollama pull {self.model})\n"
                                f"3. L'endpoint sia corretto\n"
                                f"Risposta server: {e.response.text[:200]}"
                            ) from e
                        # Altrimenti prova con 'input'
                        continue
                    else:
                        # Altri errori HTTP
                        if field_name == "input":
                            raise ValueError(
                                f"Errore HTTP {e.response.status_code} durante generazione embedding:\n"
                                f"{e.response.text[:200]}\n"
                                f"Modello: {self.model}, Campo: {field_name}"
                            ) from e
                        continue
                except requests.exceptions.ConnectionError as e:
                    raise ConnectionError(
                        f"Impossibile connettersi a Ollama su {self.base_url}.\n"
                        f"Verifica che Ollama sia in esecuzione (esegui: ollama serve)"
                    ) from e
                except Exception as e:
                    last_error = str(e)
                    if field_name == "input":
                        raise ValueError(
                            f"Errore durante generazione embedding: {last_error}\n"
                            f"Modello: {self.model}"
                        ) from e
                    continue
            else:
                # Se arriviamo qui, nessun formato ha funzionato
                raise ValueError(
                    f"Impossibile generare embedding dopo aver provato entrambi i formati.\n"
                    f"Ultimo errore: {last_error}\n"
                    f"Modello: {self.model}\n"
                    f"Verifica che il modello sia installato: ollama pull {self.model}"
                )
        return embeddings

    def get_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.dimension


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Embedding provider using OpenAI API."""

    def __init__(self, api_key: str = None, model: str = None):
        api_key = api_key or ModelConfig.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=api_key)
        self.model = model or ModelConfig.OPENAI_EMBEDDING_MODEL
        self.dimension = ModelConfig.get_embedding_dimension()

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def get_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.dimension


class GoogleEmbeddingProvider(EmbeddingProvider):
    """Embedding provider using Google Generative AI API."""

    def __init__(self, api_key: str = None, model: str = None):
        import google.generativeai as genai

        api_key = api_key or ModelConfig.GOOGLE_API_KEY
        if not api_key:
            raise ValueError("Google API key is required")
        genai.configure(api_key=api_key)
        self.genai = genai
        self.model = model or ModelConfig.GOOGLE_EMBEDDING_MODEL
        self.dimension = ModelConfig.get_embedding_dimension()

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Google API."""
        embeddings = []
        for text in texts:
            result = self.genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document",
            )
            embeddings.append(result["embedding"])
        return embeddings

    def get_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.dimension


def get_embedding_provider() -> EmbeddingProvider:
    """Factory function to get the appropriate embedding provider."""
    provider = ModelConfig.EMBEDDING_PROVIDER.lower()

    if provider == "ollama":
        return OllamaEmbeddingProvider()
    elif provider == "openai":
        return OpenAIEmbeddingProvider()
    elif provider == "google":
        return GoogleEmbeddingProvider()
    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")
