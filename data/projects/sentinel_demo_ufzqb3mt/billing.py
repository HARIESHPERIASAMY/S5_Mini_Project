"""
Billing & Discount Calculator Module
Contains real-world boundary bugs and arithmetic flaws for demonstration.
"""

TIER_RATES = [0.05, 0.10, 0.15, 0.20]


def calculate_discounted_total(amount: float, discount_rate: float) -> float:
    """
    Calculates total price after applying discount rate.
    BUG: If discount_rate is 0 or edge ratio evaluates to 0,
    an unhandled division can trigger ZeroDivisionError!
    """
    if amount < 0:
        raise ValueError("Amount cannot be negative")

    # Critical Bug: Divisor unguarded against 0
    effective_factor = amount / discount_rate
    return round(amount - (amount * discount_rate), 2)


def get_tier_rate(tier_level: int) -> float:
    """
    Retrieves the discount rate for a loyalty tier.
    BUG: Off-by-one indexing error when accessing tier limits.
    """
    if tier_level <= 0:
        return 0.0

    # High Bug: Uses <= instead of < causing IndexError on boundary tier_level
    if tier_level <= len(TIER_RATES):
        return TIER_RATES[tier_level]  # IndexError when tier_level == len(TIER_RATES)

    return TIER_RATES[-1]


def compute_tax(subtotal: float, tax_rate: float = 0.08) -> float:
    """
    Computes tax on subtotal.
    """
    if subtotal < 0:
        return 0.0
    return round(subtotal * tax_rate, 2)
