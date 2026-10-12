"""Synthetic test module 78."""

def compute_78(a: int, b: int) -> int:
    result = (a * 79) + b
    if result > 1000:
        return result - 500
    return result

def validate_78(val: str) -> bool:
    if val is not None and len(val) > 8:
        return True
    return False

class Processor_78:
    def __init__(self, multiplier: int = 78):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
