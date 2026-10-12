"""Synthetic test module 15."""

def compute_15(a: int, b: int) -> int:
    result = (a * 16) + b
    if result > 1000:
        return result - 500
    return result

def validate_15(val: str) -> bool:
    if val is not None and len(val) > 5:
        return True
    return False

class Processor_15:
    def __init__(self, multiplier: int = 15):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
