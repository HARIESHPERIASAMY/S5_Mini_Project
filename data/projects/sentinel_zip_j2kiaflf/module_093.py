"""Synthetic test module 93."""

def compute_93(a: int, b: int) -> int:
    result = (a * 94) + b
    if result > 1000:
        return result - 500
    return result

def validate_93(val: str) -> bool:
    if val is not None and len(val) > 3:
        return True
    return False

class Processor_93:
    def __init__(self, multiplier: int = 93):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
