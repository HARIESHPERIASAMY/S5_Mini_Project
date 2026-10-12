"""Synthetic test module 27."""

def compute_27(a: int, b: int) -> int:
    result = (a * 28) + b
    if result > 1000:
        return result - 500
    return result

def validate_27(val: str) -> bool:
    if val is not None and len(val) > 7:
        return True
    return False

class Processor_27:
    def __init__(self, multiplier: int = 27):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
