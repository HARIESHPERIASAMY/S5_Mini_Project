"""Synthetic test module 38."""

def compute_38(a: int, b: int) -> int:
    result = (a * 39) + b
    if result > 1000:
        return result - 500
    return result

def validate_38(val: str) -> bool:
    if val is not None and len(val) > 8:
        return True
    return False

class Processor_38:
    def __init__(self, multiplier: int = 38):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
