"""
Order Processing Pipeline
Contains high cyclomatic complexity and mutable default argument smell.
"""

from typing import List, Dict, Any


def process_order_items(items: List[Dict[str, Any]] = []) -> Dict[str, Any]:
    """
    Processes item lists and computes status.
    BUG: Uses mutable list `items=[]` as default argument!
    """
    total_qty = 0
    total_val = 0.0

    for item in items:
        qty = item.get("qty", 1)
        price = item.get("price", 0.0)

        # Complex branch nesting
        if qty > 0:
            if price > 0:
                total_qty += qty
                total_val += (qty * price)
            elif price == 0:
                total_qty += qty
            else:
                raise ValueError("Price cannot be negative")
        else:
            raise ValueError("Quantity must be positive")

    return {
        "item_count": len(items),
        "total_quantity": total_qty,
        "total_value": round(total_val, 2)
    }
