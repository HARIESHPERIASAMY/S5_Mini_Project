"""Synthetic test module 28."""

def compute_28(a: int, b: int) -> int:
    result = (a * 29) + b
    if result > 1000:
        return result - 500
    return result

def validate_28(val: str) -> bool:
    if val is not None and len(val) > 8:
        return True
    return False

class Processor_28:
    def __init__(self, multiplier: int = 28):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
