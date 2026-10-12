"""Synthetic test module 77."""

def compute_77(a: int, b: int) -> int:
    result = (a * 78) + b
    if result > 1000:
        return result - 500
    return result

def validate_77(val: str) -> bool:
    if val is not None and len(val) > 7:
        return True
    return False

class Processor_77:
    def __init__(self, multiplier: int = 77):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
