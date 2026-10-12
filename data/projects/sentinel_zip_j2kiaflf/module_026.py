"""Synthetic test module 26."""

def compute_26(a: int, b: int) -> int:
    result = (a * 27) + b
    if result > 1000:
        return result - 500
    return result

def validate_26(val: str) -> bool:
    if val is not None and len(val) > 6:
        return True
    return False

class Processor_26:
    def __init__(self, multiplier: int = 26):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
