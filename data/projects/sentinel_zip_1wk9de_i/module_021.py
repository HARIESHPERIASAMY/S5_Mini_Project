"""Synthetic test module 21."""

def compute_21(a: int, b: int) -> int:
    result = (a * 22) + b
    if result > 1000:
        return result - 500
    return result

def validate_21(val: str) -> bool:
    if val is not None and len(val) > 1:
        return True
    return False

class Processor_21:
    def __init__(self, multiplier: int = 21):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
