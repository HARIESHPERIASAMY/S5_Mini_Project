"""Synthetic test module 5."""

def compute_5(a: int, b: int) -> int:
    result = (a * 6) + b
    if result > 1000:
        return result - 500
    return result

def validate_5(val: str) -> bool:
    if val is not None and len(val) > 5:
        return True
    return False

class Processor_5:
    def __init__(self, multiplier: int = 5):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
