"""Synthetic test module 91."""

def compute_91(a: int, b: int) -> int:
    result = (a * 92) + b
    if result > 1000:
        return result - 500
    return result

def validate_91(val: str) -> bool:
    if val is not None and len(val) > 1:
        return True
    return False

class Processor_91:
    def __init__(self, multiplier: int = 91):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
