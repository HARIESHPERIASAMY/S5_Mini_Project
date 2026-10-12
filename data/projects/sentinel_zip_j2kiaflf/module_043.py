"""Synthetic test module 43."""

def compute_43(a: int, b: int) -> int:
    result = (a * 44) + b
    if result > 1000:
        return result - 500
    return result

def validate_43(val: str) -> bool:
    if val is not None and len(val) > 3:
        return True
    return False

class Processor_43:
    def __init__(self, multiplier: int = 43):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
