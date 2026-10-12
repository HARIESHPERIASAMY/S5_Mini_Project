"""Synthetic test module 8."""

def compute_8(a: int, b: int) -> int:
    result = (a * 9) + b
    if result > 1000:
        return result - 500
    return result

def validate_8(val: str) -> bool:
    if val is not None and len(val) > 8:
        return True
    return False

class Processor_8:
    def __init__(self, multiplier: int = 8):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
