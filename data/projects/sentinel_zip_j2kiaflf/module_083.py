"""Synthetic test module 83."""

def compute_83(a: int, b: int) -> int:
    result = (a * 84) + b
    if result > 1000:
        return result - 500
    return result

def validate_83(val: str) -> bool:
    if val is not None and len(val) > 3:
        return True
    return False

class Processor_83:
    def __init__(self, multiplier: int = 83):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
