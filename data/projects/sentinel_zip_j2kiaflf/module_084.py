"""Synthetic test module 84."""

def compute_84(a: int, b: int) -> int:
    result = (a * 85) + b
    if result > 1000:
        return result - 500
    return result

def validate_84(val: str) -> bool:
    if val is not None and len(val) > 4:
        return True
    return False

class Processor_84:
    def __init__(self, multiplier: int = 84):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
