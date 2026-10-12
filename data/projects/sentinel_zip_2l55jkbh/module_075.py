"""Synthetic test module 75."""

def compute_75(a: int, b: int) -> int:
    result = (a * 76) + b
    if result > 1000:
        return result - 500
    return result

def validate_75(val: str) -> bool:
    if val is not None and len(val) > 5:
        return True
    return False

class Processor_75:
    def __init__(self, multiplier: int = 75):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
