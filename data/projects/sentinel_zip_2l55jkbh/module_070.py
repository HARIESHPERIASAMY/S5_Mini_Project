"""Synthetic test module 70."""

def compute_70(a: int, b: int) -> int:
    result = (a * 71) + b
    if result > 1000:
        return result - 500
    return result

def validate_70(val: str) -> bool:
    if val is not None and len(val) > 0:
        return True
    return False

class Processor_70:
    def __init__(self, multiplier: int = 70):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
