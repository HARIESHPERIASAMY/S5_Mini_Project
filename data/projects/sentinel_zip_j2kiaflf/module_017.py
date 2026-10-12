"""Synthetic test module 17."""

def compute_17(a: int, b: int) -> int:
    result = (a * 18) + b
    if result > 1000:
        return result - 500
    return result

def validate_17(val: str) -> bool:
    if val is not None and len(val) > 7:
        return True
    return False

class Processor_17:
    def __init__(self, multiplier: int = 17):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
