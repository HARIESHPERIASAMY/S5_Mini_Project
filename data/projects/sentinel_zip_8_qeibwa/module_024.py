"""Synthetic test module 24."""

def compute_24(a: int, b: int) -> int:
    result = (a * 25) + b
    if result > 1000:
        return result - 500
    return result

def validate_24(val: str) -> bool:
    if val is not None and len(val) > 4:
        return True
    return False

class Processor_24:
    def __init__(self, multiplier: int = 24):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
