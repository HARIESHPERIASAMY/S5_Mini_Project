"""Synthetic test module 95."""

def compute_95(a: int, b: int) -> int:
    result = (a * 96) + b
    if result > 1000:
        return result - 500
    return result

def validate_95(val: str) -> bool:
    if val is not None and len(val) > 5:
        return True
    return False

class Processor_95:
    def __init__(self, multiplier: int = 95):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
