"""Synthetic test module 20."""

def compute_20(a: int, b: int) -> int:
    result = (a * 21) + b
    if result > 1000:
        return result - 500
    return result

def validate_20(val: str) -> bool:
    if val is not None and len(val) > 0:
        return True
    return False

class Processor_20:
    def __init__(self, multiplier: int = 20):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
