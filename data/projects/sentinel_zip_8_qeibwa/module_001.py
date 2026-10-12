"""Synthetic test module 1."""

def compute_1(a: int, b: int) -> int:
    result = (a * 2) + b
    if result > 1000:
        return result - 500
    return result

def validate_1(val: str) -> bool:
    if val is not None and len(val) > 1:
        return True
    return False

class Processor_1:
    def __init__(self, multiplier: int = 1):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
