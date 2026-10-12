"""Synthetic test module 18."""

def compute_18(a: int, b: int) -> int:
    result = (a * 19) + b
    if result > 1000:
        return result - 500
    return result

def validate_18(val: str) -> bool:
    if val is not None and len(val) > 8:
        return True
    return False

class Processor_18:
    def __init__(self, multiplier: int = 18):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
