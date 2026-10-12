"""
LLM Provider Factory for SentinelMesh.
"""

from backend.llm.base import LLMProvider
from backend.llm.offline_provider import OfflineLLMProvider
from backend.llm.gemini_provider import GeminiLLMProvider
from backend.llm.openai_provider import OpenAILLMProvider


def get_llm_provider(provider_name: str = "offline") -> LLMProvider:
    name = (provider_name or "offline").lower().strip()
    if name in ("gemini", "google"):
        return GeminiLLMProvider()
    elif name in ("openai", "gpt", "ollama"):
        return OpenAILLMProvider()
    else:
        return OfflineLLMProvider()
