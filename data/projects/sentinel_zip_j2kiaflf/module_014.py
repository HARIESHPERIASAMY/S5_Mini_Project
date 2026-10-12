"""Synthetic test module 14."""

def compute_14(a: int, b: int) -> int:
    result = (a * 15) + b
    if result > 1000:
        return result - 500
    return result

def validate_14(val: str) -> bool:
    if val is not None and len(val) > 4:
        return True
    return False

class Processor_14:
    def __init__(self, multiplier: int = 14):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
