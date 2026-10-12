"""
OpenAI & Ollama-compatible LLM Provider for SentinelMesh.
Supports standard OpenAI endpoints and local Ollama (`http://localhost:11434/v1`).
Falls back seamlessly to OfflineLLMProvider.
"""

import os
import json
from typing import Optional, Dict, Any, List
import httpx
from backend.llm.base import LLMProvider
from backend.llm.offline_provider import OfflineLLMProvider


class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "ollama")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.offline = OfflineLLMProvider()

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json={"model": self.model, "messages": messages, "temperature": 0.2}
                )
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
        except Exception:
            pass

        return await self.offline.generate_text(prompt, system_prompt, **kwargs)

    async def analyze_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        prompt = (
            "Analyze the following Python code for bugs and security flaws. "
            "Output JSON with a 'smells' array: [{line, type, severity, category, desc}]:\n\n"
            f"```python\n{code}\n```"
        )
        try:
            raw = await self.generate_text(prompt)
            clean = raw.strip()
            if "```json" in clean:
                clean = clean.split("```json")[1].split("```")[0].strip()
            elif "```" in clean:
                clean = clean.split("```")[1].split("```")[0].strip()
            return json.loads(clean)
        except Exception:
            return await self.offline.analyze_code(code, context)

    async def generate_tests(self, code: str, filename: str, context: Optional[Dict[str, Any]] = None) -> str:
        prompt = (
            f"Write standalone pytest tests for {filename} targeting edge-cases, nulls, and boundary conditions.\n"
            f"```python\n{code}\n```"
        )
        try:
            raw = await self.generate_text(prompt)
            if "```python" in raw:
                return raw.split("```python")[1].split("```")[0].strip()
            return raw.strip()
        except Exception:
            return await self.offline.generate_tests(code, filename, context)

    async def generate_patch(self, code: str, bug_description: str, file_path: str) -> str:
        return await self.offline.generate_patch(code, bug_description, file_path)

    async def explain_bug(self, bug_title: str, code_snippet: str, causal_chain: List[str]) -> str:
        return await self.offline.explain_bug(bug_title, code_snippet, causal_chain)
