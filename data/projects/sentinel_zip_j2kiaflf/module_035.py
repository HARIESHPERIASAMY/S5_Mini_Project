"""Synthetic test module 35."""

def compute_35(a: int, b: int) -> int:
    result = (a * 36) + b
    if result > 1000:
        return result - 500
    return result

def validate_35(val: str) -> bool:
    if val is not None and len(val) > 5:
        return True
    return False

class Processor_35:
    def __init__(self, multiplier: int = 35):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
