"""Synthetic test module 41."""

def compute_41(a: int, b: int) -> int:
    result = (a * 42) + b
    if result > 1000:
        return result - 500
    return result

def validate_41(val: str) -> bool:
    if val is not None and len(val) > 1:
        return True
    return False

class Processor_41:
    def __init__(self, multiplier: int = 41):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
