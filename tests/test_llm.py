"""
Tests for Pluggable LLM Layer and Offline Provider.
"""

import pytest
from backend.llm import get_llm_provider
from backend.llm.offline_provider import OfflineLLMProvider


@pytest.mark.asyncio
async def test_offline_provider_factory():
    provider = get_llm_provider("offline")
    assert isinstance(provider, OfflineLLMProvider)


@pytest.mark.asyncio
async def test_offline_analyze_code():
    code = """
def bad_div(a, b):
    return a / 0

def bad_sql(query_input):
    db.execute(f"SELECT * FROM items WHERE id = '{query_input}'")
"""
    provider = OfflineLLMProvider()
    res = await provider.analyze_code(code)
    assert "smells" in res
    smell_types = [s["type"] for s in res["smells"]]
    assert "ZeroDivisionError" in smell_types
    assert "SQLInjectionRisk" in smell_types


@pytest.mark.asyncio
async def test_offline_generate_tests():
    code = """
def add(a, b):
    return a + b
"""
    provider = OfflineLLMProvider()
    tests_str = await provider.generate_tests(code, "calc.py")
    assert "def test_add_nominal():" in tests_str
    assert "def test_add_boundary_and_edge_cases():" in tests_str
    assert "pytest" in tests_str


@pytest.mark.asyncio
async def test_offline_generate_patch():
    code = """
def calc(amount, discount):
    return amount / discount
"""
    provider = OfflineLLMProvider()
    diff = await provider.generate_patch(code, "ZeroDivisionError: division by zero", "calc.py")
    assert "---" in diff or "+++" in diff or "discount == 0" in diff

    # Exercise explain_bug and various bug types in generate_patch
    explanation = await provider.explain_bug("ZeroDivision", code, ["step 1", "step 2"])
    assert "safety check" in explanation.lower()

    # SQL patch
    sql_code = 'db.execute(f"SELECT * FROM users WHERE username = \'{username}\'")'
    diff_sql = await provider.generate_patch(sql_code, "sql injection risk", "db.py")
    assert "Sanitized" in diff_sql or "---" in diff_sql

    # Index error patch
    idx_code = 'if i <= len(items): return items[i]'
    diff_idx = await provider.generate_patch(idx_code, "indexerror in bounds check", "list.py")
    assert "---" in diff_idx or "<" in diff_idx

    # NoneType patch
    none_code = 'def process(value):\n    return value.strip()'
    diff_none = await provider.generate_patch(none_code, "nonetype attribute error", "util.py")
    assert "cannot be None" in diff_none or "---" in diff_none



@pytest.mark.asyncio
async def test_gemini_and_openai_providers_with_mocked_llm(monkeypatch):
    from backend.llm.gemini_provider import GeminiLLMProvider
    from backend.llm.openai_provider import OpenAILLMProvider

    # Mock generate_text to return valid mock outputs
    async def mock_gen_text(self, prompt, **kwargs):
        if "analyze" in prompt.lower() or "smells" in prompt.lower():
            return '```json\n{"smells": [{"line": 1, "type": "MockBug", "severity": "HIGH", "category": "LOGIC", "desc": "Mock bug"}]}\n```'
        if "pytest" in prompt.lower():
            return '```python\ndef test_mock(): assert True\n```'
        if "diff" in prompt.lower():
            return '```diff\n--- a/f.py\n+++ b/f.py\n@@ -1 +1 @@\n- old\n+ new\n```'
        return "This is a beginner explanation of the bug."

    monkeypatch.setattr(GeminiLLMProvider, "generate_text", mock_gen_text)
    monkeypatch.setattr(OpenAILLMProvider, "generate_text", mock_gen_text)

    # 1. Gemini provider
    gemini = GeminiLLMProvider(api_key="mock_key")
    res_analysis = await gemini.analyze_code("x = 1")
    assert "smells" in res_analysis
    assert res_analysis["smells"][0]["type"] == "MockBug"

    res_tests = await gemini.generate_tests("x = 1", "test.py")
    assert "def test_mock():" in res_tests

    res_patch = await gemini.generate_patch("x = 1", "bug", "f.py")
    assert "--- a/f.py" in res_patch

    res_exp = await gemini.explain_bug("bug", "x = 1", ["step1"])
    assert "beginner explanation" in res_exp

    # 2. OpenAI provider
    openai_p = OpenAILLMProvider(api_key="mock_key")
    res_oa_analysis = await openai_p.analyze_code("x = 1")
    assert "smells" in res_oa_analysis

    res_oa_tests = await openai_p.generate_tests("x = 1", "test.py")
    assert "def test_mock():" in res_oa_tests

    res_oa_patch = await openai_p.generate_patch("x = 1", "bug", "f.py")
    assert "--- a/f.py" in res_oa_patch

