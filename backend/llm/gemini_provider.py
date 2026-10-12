"""
Google Gemini LLM Provider for SentinelMesh.
Uses GEMINI_API_KEY if present; seamlessly delegates to OfflineLLMProvider as fallback.
"""

import os
import json
from typing import Optional, Dict, Any, List
import httpx
from backend.llm.base import LLMProvider
from backend.llm.offline_provider import OfflineLLMProvider


class GeminiLLMProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.offline = OfflineLLMProvider()
        self.model = "gemini-2.5-flash"

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        if not self.api_key:
            return await self.offline.generate_text(prompt, system_prompt, **kwargs)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System Instructions: {system_prompt}"}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json={"contents": contents})
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
        except Exception:
            pass

        return await self.offline.generate_text(prompt, system_prompt, **kwargs)

    async def analyze_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.api_key:
            return await self.offline.analyze_code(code, context)
        try:
            prompt = (
                "Analyze the following Python code for bugs, security vulnerabilities, and logic flaws. "
                "Respond in valid JSON with key 'smells' containing an array of objects with: "
                "line, type, severity (CRITICAL, HIGH, MEDIUM, LOW), category, and desc.\n\n"
                f"```python\n{code}\n```"
            )
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
        if not self.api_key:
            return await self.offline.generate_tests(code, filename, context)
        try:
            prompt = (
                f"Write a comprehensive, standalone pytest test suite for `{filename}`. "
                "Include unit tests, edge-cases, null handling, and property boundary checks. "
                "Output ONLY executable python code enclosed in ```python and ```.\n\n"
                f"```python\n{code}\n```"
            )
            raw = await self.generate_text(prompt)
            if "```python" in raw:
                return raw.split("```python")[1].split("```")[0].strip()
            return raw.strip()
        except Exception:
            return await self.offline.generate_tests(code, filename, context)

    async def generate_patch(self, code: str, bug_description: str, file_path: str) -> str:
        if not self.api_key:
            return await self.offline.generate_patch(code, bug_description, file_path)
        try:
            prompt = (
                f"Generate a unified diff patch (`diff -u`) to fix this bug: '{bug_description}' in `{file_path}`.\n"
                f"Original code:\n```python\n{code}\n```\n"
                "Return ONLY the unified diff."
            )
            raw = await self.generate_text(prompt)
            if "```diff" in raw:
                return raw.split("```diff")[1].split("```")[0].strip()
            return raw.strip()
        except Exception:
            return await self.offline.generate_patch(code, bug_description, file_path)

    async def explain_bug(self, bug_title: str, code_snippet: str, causal_chain: List[str]) -> str:
        if not self.api_key:
            return await self.offline.explain_bug(bug_title, code_snippet, causal_chain)
        try:
            prompt = (
                f"Explain this software bug like I am a beginner:\n"
                f"Title: {bug_title}\n"
                f"Causal steps: {causal_chain}\n"
                f"Code:\n```python\n{code_snippet}\n```\n"
                "Use a helpful analogy and explain what happened step by step."
            )
            return await self.generate_text(prompt)
        except Exception:
            return await self.offline.explain_bug(bug_title, code_snippet, causal_chain)
