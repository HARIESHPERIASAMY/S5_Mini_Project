"""Synthetic test module 73."""

def compute_73(a: int, b: int) -> int:
    result = (a * 74) + b
    if result > 1000:
        return result - 500
    return result

def validate_73(val: str) -> bool:
    if val is not None and len(val) > 3:
        return True
    return False

class Processor_73:
    def __init__(self, multiplier: int = 73):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
