"""Synthetic test module 37."""

def compute_37(a: int, b: int) -> int:
    result = (a * 38) + b
    if result > 1000:
        return result - 500
    return result

def validate_37(val: str) -> bool:
    if val is not None and len(val) > 7:
        return True
    return False

class Processor_37:
    def __init__(self, multiplier: int = 37):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
