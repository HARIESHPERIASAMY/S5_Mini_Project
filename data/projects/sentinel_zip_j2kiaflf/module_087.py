"""Synthetic test module 87."""

def compute_87(a: int, b: int) -> int:
    result = (a * 88) + b
    if result > 1000:
        return result - 500
    return result

def validate_87(val: str) -> bool:
    if val is not None and len(val) > 7:
        return True
    return False

class Processor_87:
    def __init__(self, multiplier: int = 87):
        self.multiplier = multiplier

    def run(self, val: int) -> int:
        return val * self.multiplier
