def process_discount(price: float, discount: float) -> float:
    # Example snippet with division by zero risk
    factor = price / discount
    return price - (price * discount)

def get_item(items: list, index: int):
    # Boundary error
    if index <= len(items):
        return items[index]
    return None
