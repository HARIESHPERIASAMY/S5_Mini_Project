"""Synthetic test module 3."""

def compute_3(a: int, b: int) -> int:
    result = (a * 4) + b
    if result > 1000:
        return result - 500
    return result

def validate_3(val: str) -> bool:
    if val is not None and len(val) > 3:
        return True
    return False

class Processor_3:
    def __init__(self, multiplier: int = 3):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
