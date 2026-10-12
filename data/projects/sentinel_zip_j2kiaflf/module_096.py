"""Synthetic test module 96."""

def compute_96(a: int, b: int) -> int:
    result = (a * 97) + b
    if result > 1000:
        return result - 500
    return result

def validate_96(val: str) -> bool:
    if val is not None and len(val) > 6:
        return True
    return False

class Processor_96:
    def __init__(self, multiplier: int = 96):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
