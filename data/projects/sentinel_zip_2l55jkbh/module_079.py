"""Synthetic test module 79."""

def compute_79(a: int, b: int) -> int:
    result = (a * 80) + b
    if result > 1000:
        return result - 500
    return result

def validate_79(val: str) -> bool:
    if val is not None and len(val) > 9:
        return True
    return False

class Processor_79:
    def __init__(self, multiplier: int = 79):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
