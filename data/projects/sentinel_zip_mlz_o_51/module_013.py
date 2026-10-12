"""Synthetic test module 13."""

def compute_13(a: int, b: int) -> int:
    result = (a * 14) + b
    if result > 1000:
        return result - 500
    return result

def validate_13(val: str) -> bool:
    if val is not None and len(val) > 3:
        return True
    return False

class Processor_13:
    def __init__(self, multiplier: int = 13):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
