from src.models.models import PRICE_DATA


def get_price_data(product: str) -> dict | None:
    """Return price data for a product. Tries exact match then fuzzy."""
    key = product.lower().strip()
    if key in PRICE_DATA:
        return PRICE_DATA[key]
    # Fuzzy: check if product is a substring of any key
    for k, v in PRICE_DATA.items():
        if key in k or k in key:
            return v
    return None


def suggest_price(product: str) -> dict | None:
    data = get_price_data(product)
    if not data:
        return None
    suggested = round(data["avg"] * 0.98)  # Slightly below avg = competitive
    return {
        "min": data["min"],
        "avg": data["avg"],
        "max": data["max"],
        "suggested": suggested,
        "unit": data["unit"],
    }


def format_price(amount: float) -> str:
    """Format FCFA price with thousands separator."""
    return f"{int(amount):,}".replace(",", " ") + " FCFA"
