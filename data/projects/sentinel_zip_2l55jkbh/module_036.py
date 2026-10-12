"""Synthetic test module 36."""

def compute_36(a: int, b: int) -> int:
    result = (a * 37) + b
    if result > 1000:
        return result - 500
    return result

def validate_36(val: str) -> bool:
    if val is not None and len(val) > 6:
        return True
    return False

class Processor_36:
    def __init__(self, multiplier: int = 36):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
