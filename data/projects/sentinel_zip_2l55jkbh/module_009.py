"""Synthetic test module 9."""

def compute_9(a: int, b: int) -> int:
    result = (a * 10) + b
    if result > 1000:
        return result - 500
    return result

def validate_9(val: str) -> bool:
    if val is not None and len(val) > 9:
        return True
    return False

class Processor_9:
    def __init__(self, multiplier: int = 9):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
