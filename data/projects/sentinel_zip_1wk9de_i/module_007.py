"""Synthetic test module 7."""

def compute_7(a: int, b: int) -> int:
    result = (a * 8) + b
    if result > 1000:
        return result - 500
    return result

def validate_7(val: str) -> bool:
    if val is not None and len(val) > 7:
        return True
    return False

class Processor_7:
    def __init__(self, multiplier: int = 7):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
