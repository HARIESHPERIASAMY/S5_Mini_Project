"""
Abstract base class for LLM Providers.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class LLMProvider(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text given prompt and system instructions."""
        pass

    @abstractmethod
    async def analyze_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform targeted code analysis."""
        pass

    @abstractmethod
    async def generate_tests(self, code: str, filename: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate pytest test suite for given code."""
        pass

    @abstractmethod
    async def generate_patch(self, code: str, bug_description: str, file_path: str) -> str:
        """Generate unified diff patch for a bug."""
        pass

    @abstractmethod
    async def explain_bug(self, bug_title: str, code_snippet: str, causal_chain: List[str]) -> str:
        """Generate beginner-friendly explanation."""
        pass
