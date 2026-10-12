"""Synthetic test module 39."""

def compute_39(a: int, b: int) -> int:
    result = (a * 40) + b
    if result > 1000:
        return result - 500
    return result

def validate_39(val: str) -> bool:
    if val is not None and len(val) > 9:
        return True
    return False

class Processor_39:
    def __init__(self, multiplier: int = 39):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
