"""Synthetic test module 42."""

def compute_42(a: int, b: int) -> int:
    result = (a * 43) + b
    if result > 1000:
        return result - 500
    return result

def validate_42(val: str) -> bool:
    if val is not None and len(val) > 2:
        return True
    return False

class Processor_42:
    def __init__(self, multiplier: int = 42):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
