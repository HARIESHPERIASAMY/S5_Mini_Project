"""Synthetic test module 80."""

def compute_80(a: int, b: int) -> int:
    result = (a * 81) + b
    if result > 1000:
        return result - 500
    return result

def validate_80(val: str) -> bool:
    if val is not None and len(val) > 0:
        return True
    return False

class Processor_80:
    def __init__(self, multiplier: int = 80):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
