"""LLM provider implementations."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import requests
import os
from inngest.experimental import ai
from config import ModelConfig

# ============================================================================
# CONSTANTS - API timeout settings
# ============================================================================
DEFAULT_LLM_TIMEOUT = 240  # Timeout per richieste LLM API (secondi) - modelli locali possono richiedere più tempo

# ============================================================================
# CONSTANTS - LLM generation defaults (usati come fallback se non specificati)
# ============================================================================
DEFAULT_MAX_TOKENS = 1024  # Numero massimo di token da generare
DEFAULT_TEMPERATURE = 0.2  # Temperatura per generazione (0.0-1.0)


class LLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    def get_inngest_adapter(self):
        """Get an inngest adapter if supported, otherwise None."""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> str:
        """Generate a response from the LLM."""
        pass


class OllamaLLMProvider(LLMProvider):
    """LLM provider using Ollama API."""

    def __init__(
        self,
        base_url: str = None,
        model: str = None,
    ):
        self.base_url = base_url or ModelConfig.OLLAMA_BASE_URL
        self.model = model or ModelConfig.OLLAMA_LLM_MODEL

    def get_inngest_adapter(self):
        """Ollama doesn't have a native inngest adapter, return None."""
        return None

    async def generate(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> str:
        """Generate a response using Ollama API."""
        import asyncio

        # Convert messages to Ollama chat format
        ollama_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            # Ollama chat API accetta "system", "user", "assistant"
            if role in ["system", "user", "assistant"]:
                ollama_messages.append({"role": role, "content": content})

        # Run the synchronous request in a thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": ollama_messages,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature,
                    },
                    "stream": False,
                },
                timeout=DEFAULT_LLM_TIMEOUT,
            ),
        )
        response.raise_for_status()
        result = response.json()
        # L'API chat restituisce message.content invece di response
        message = result.get("message", {})
        return message.get("content", "").strip()


class OpenAILLMProvider(LLMProvider):
    """LLM provider using OpenAI API."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or ModelConfig.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        self.model = model or ModelConfig.OPENAI_LLM_MODEL

    def get_inngest_adapter(self):
        """Get the inngest OpenAI adapter."""
        return ai.openai.Adapter(auth_key=self.api_key, model=self.model)

    async def generate(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> str:
        """Generate a response using OpenAI API (via inngest adapter)."""
        # This is typically called through inngest, but we can also call directly
        # For direct calls, we'd use the OpenAI client, but since we have inngest,
        # we'll rely on the adapter being used in the inngest context
        raise NotImplementedError(
            "OpenAI generation should be done through inngest adapter"
        )


class GoogleLLMProvider(LLMProvider):
    """LLM provider using Google Gemini API."""

    def __init__(self, api_key: str = None, model: str = None):
        import google.generativeai as genai

        self.api_key = api_key or ModelConfig.GOOGLE_API_KEY
        if not self.api_key:
            raise ValueError("Google API key is required")
        genai.configure(api_key=self.api_key)
        self.model_name = model or ModelConfig.GOOGLE_LLM_MODEL
        self.genai = genai
        self.model = genai.GenerativeModel(self.model_name)

    def get_inngest_adapter(self):
        """Google doesn't have a native inngest adapter, return None."""
        return None

    async def generate(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> str:
        """Generate a response using Google Gemini API."""
        # Convert messages to Google format
        # Google expects alternating user/assistant messages
        chat = self.model.start_chat(history=[])

        # Find system message if present
        system_content = None
        user_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_content = msg.get("content", "")
            elif msg.get("role") == "user":
                user_messages.append(msg.get("content", ""))

        # Send all user messages
        full_prompt = "\n\n".join(user_messages)
        if system_content:
            full_prompt = f"{system_content}\n\n{full_prompt}"

        import asyncio

        # Run the synchronous call in a thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.model.generate_content(
                full_prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": temperature,
                },
            ),
        )
        return response.text.strip()


class AnthropicLLMProvider(LLMProvider):
    """LLM provider using Anthropic Claude API."""

    def __init__(self, api_key: str = None, model: str = None):
        from anthropic import Anthropic

        self.api_key = api_key or ModelConfig.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        self.client = Anthropic(api_key=self.api_key)
        self.model = model or ModelConfig.ANTHROPIC_LLM_MODEL

    def get_inngest_adapter(self):
        """Anthropic doesn't have a native inngest adapter, return None."""
        return None

    async def generate(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> str:
        """Generate a response using Anthropic Claude API."""
        import asyncio

        # Separate system message from conversation messages
        system_message = None
        conversation_messages = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                system_message = content
            elif role in ["user", "assistant"]:
                conversation_messages.append({"role": role, "content": content})

        # Run the synchronous call in a thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message or "",
                messages=conversation_messages,
            ),
        )

        # Extract text from the response
        if response.content and len(response.content) > 0:
            return response.content[0].text.strip()
        return ""


def get_llm_provider() -> LLMProvider:
    """Factory function to get the appropriate LLM provider."""
    provider = ModelConfig.LLM_PROVIDER.lower()

    if provider == "ollama":
        return OllamaLLMProvider()
    elif provider == "openai":
        return OpenAILLMProvider()
    elif provider == "google":
        return GoogleLLMProvider()
    elif provider == "anthropic":
        return AnthropicLLMProvider()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
