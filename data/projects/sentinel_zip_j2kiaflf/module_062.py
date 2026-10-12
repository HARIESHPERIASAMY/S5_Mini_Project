"""Synthetic test module 62."""

def compute_62(a: int, b: int) -> int:
    result = (a * 63) + b
    if result > 1000:
        return result - 500
    return result

def validate_62(val: str) -> bool:
    if val is not None and len(val) > 2:
        return True
    return False

class Processor_62:
    def __init__(self, multiplier: int = 62):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
