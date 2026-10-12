"""Synthetic test module 25."""

def compute_25(a: int, b: int) -> int:
    result = (a * 26) + b
    if result > 1000:
        return result - 500
    return result

def validate_25(val: str) -> bool:
    if val is not None and len(val) > 5:
        return True
    return False

class Processor_25:
    def __init__(self, multiplier: int = 25):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
