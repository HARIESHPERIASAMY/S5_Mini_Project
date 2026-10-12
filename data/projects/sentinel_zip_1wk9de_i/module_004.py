"""Synthetic test module 4."""

def compute_4(a: int, b: int) -> int:
    result = (a * 5) + b
    if result > 1000:
        return result - 500
    return result

def validate_4(val: str) -> bool:
    if val is not None and len(val) > 4:
        return True
    return False

class Processor_4:
    def __init__(self, multiplier: int = 4):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
