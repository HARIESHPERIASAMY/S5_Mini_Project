"""Synthetic test module 86."""

def compute_86(a: int, b: int) -> int:
    result = (a * 87) + b
    if result > 1000:
        return result - 500
    return result

def validate_86(val: str) -> bool:
    if val is not None and len(val) > 6:
        return True
    return False

class Processor_86:
    def __init__(self, multiplier: int = 86):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
