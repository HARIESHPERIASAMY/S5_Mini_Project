"""Synthetic test module 72."""

def compute_72(a: int, b: int) -> int:
    result = (a * 73) + b
    if result > 1000:
        return result - 500
    return result

def validate_72(val: str) -> bool:
    if val is not None and len(val) > 2:
        return True
    return False

class Processor_72:
    def __init__(self, multiplier: int = 72):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
