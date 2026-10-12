"""
Inventory and Stock Management Service
Contains state-corruption and negative balance bugs.
"""

from typing import Dict


class InventoryManager:
    def __init__(self):
        self.stock: Dict[str, int] = {
            "SKU_LAPTOP": 10,
            "SKU_PHONE": 25,
            "SKU_HEADPHONES": 5
        }

    def deduct_stock(self, sku: str, quantity: int) -> bool:
        """
        Deducts stock for an order item.
        BUG: Does not verify if quantity > stock, allowing negative inventory corruption!
        """
        if sku not in self.stock:
            return False

        # Bug: Missing guard `if self.stock[sku] < quantity: return False`
        self.stock[sku] -= quantity
        return True

    def get_stock(self, sku: str) -> int:
        return self.stock.get(sku, 0)
