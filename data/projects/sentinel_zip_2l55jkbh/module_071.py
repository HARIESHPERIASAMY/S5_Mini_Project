"""Synthetic test module 71."""

def compute_71(a: int, b: int) -> int:
    result = (a * 72) + b
    if result > 1000:
        return result - 500
    return result

def validate_71(val: str) -> bool:
    if val is not None and len(val) > 1:
        return True
    return False

class Processor_71:
    def __init__(self, multiplier: int = 71):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
