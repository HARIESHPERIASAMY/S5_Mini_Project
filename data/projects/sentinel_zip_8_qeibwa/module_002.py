"""Synthetic test module 2."""

def compute_2(a: int, b: int) -> int:
    result = (a * 3) + b
    if result > 1000:
        return result - 500
    return result

def validate_2(val: str) -> bool:
    if val is not None and len(val) > 2:
        return True
    return False

class Processor_2:
    def __init__(self, multiplier: int = 2):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
