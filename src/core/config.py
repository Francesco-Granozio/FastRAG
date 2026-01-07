"""Configuration management for LLM and embedding providers."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class ModelConfig:
    """Manages configuration for LLM and embedding providers."""

    # LLM Provider settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai").lower()
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_LLM_MODEL: str = os.getenv("OLLAMA_LLM_MODEL", "llama3:8b")

    # Embedding Provider settings
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "openai").lower()
    OLLAMA_EMBEDDING_MODEL: str = os.getenv(
        "OLLAMA_EMBEDDING_MODEL", "embeddinggemma:latest"
    )

    # Embedding dimensions (provider-specific)
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "3072"))

    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    # OpenAI specific
    OPENAI_LLM_MODEL: str = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-large"
    )

    # Google specific
    GOOGLE_LLM_MODEL: str = os.getenv("GOOGLE_LLM_MODEL", "gemini-pro")
    GOOGLE_EMBEDDING_MODEL: str = os.getenv(
        "GOOGLE_EMBEDDING_MODEL", "models/embedding-001"
    )

    # Anthropic specific
    ANTHROPIC_LLM_MODEL: str = os.getenv(
        "ANTHROPIC_LLM_MODEL", "claude-3-5-sonnet-20241022"
    )

    @classmethod
    def get_embedding_dimension(cls) -> int:
        """Get the embedding dimension based on the current provider."""
        if cls.EMBEDDING_PROVIDER == "ollama":
            # EmbeddingGemma:300M default is 768
            return int(os.getenv("EMBEDDING_DIMENSION", "768"))
        elif cls.EMBEDDING_PROVIDER == "openai":
            # OpenAI text-embedding-3-large is 3072
            return int(os.getenv("EMBEDDING_DIMENSION", "3072"))
        elif cls.EMBEDDING_PROVIDER == "google":
            # Google embedding-001 is 768
            return int(os.getenv("EMBEDDING_DIMENSION", "768"))
        else:
            return cls.EMBEDDING_DIMENSION

    @classmethod
    def validate(cls) -> None:
        """Validate the current configuration."""
        valid_llm_providers = {"ollama", "openai", "google", "anthropic"}
        valid_embedding_providers = {"ollama", "openai", "google"}

        if cls.LLM_PROVIDER not in valid_llm_providers:
            raise ValueError(
                f"Invalid LLM_PROVIDER: {cls.LLM_PROVIDER}. "
                f"Must be one of {valid_llm_providers}"
            )

        if cls.EMBEDDING_PROVIDER not in valid_embedding_providers:
            raise ValueError(
                f"Invalid EMBEDDING_PROVIDER: {cls.EMBEDDING_PROVIDER}. "
                f"Must be one of {valid_embedding_providers}"
            )

        # Validate API keys for non-Ollama providers
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")

        if cls.LLM_PROVIDER == "google" and not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required when LLM_PROVIDER=google")

        if cls.LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic"
            )

        if cls.EMBEDDING_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai"
            )

        if cls.EMBEDDING_PROVIDER == "google" and not cls.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY is required when EMBEDDING_PROVIDER=google"
            )
