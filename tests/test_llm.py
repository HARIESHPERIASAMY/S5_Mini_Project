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
