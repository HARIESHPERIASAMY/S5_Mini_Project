"""Synthetic test module 76."""

def compute_76(a: int, b: int) -> int:
    result = (a * 77) + b
    if result > 1000:
        return result - 500
    return result

def validate_76(val: str) -> bool:
    if val is not None and len(val) > 6:
        return True
    return False

class Processor_76:
    def __init__(self, multiplier: int = 76):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
