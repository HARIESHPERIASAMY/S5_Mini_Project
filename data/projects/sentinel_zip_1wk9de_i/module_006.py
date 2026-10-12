"""Synthetic test module 6."""

def compute_6(a: int, b: int) -> int:
    result = (a * 7) + b
    if result > 1000:
        return result - 500
    return result

def validate_6(val: str) -> bool:
    if val is not None and len(val) > 6:
        return True
    return False

class Processor_6:
    def __init__(self, multiplier: int = 6):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
