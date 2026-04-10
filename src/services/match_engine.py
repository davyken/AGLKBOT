from src.models.models import get_active_listings, get_user


async def find_matches(db, product: str, quantity: int, location: str = None, buyer_id: int = None) -> list:
    """Find active listings matching buyer request, excluding buyer's own listings."""
    print(f"[DEBUG] Searching for product: '{product}', location: '{location}', buyer_id: {buyer_id}")
    
    # Get all active listings first (no location filter for broader search)
    listings = await get_active_listings(db, product, None)
    
    print(f"[DEBUG] Found {len(listings)} listings before filtering")
    for l in listings:
        print(f"  - {l.get('product')} by farmer {l.get('farmerId')} at {l.get('location')}")
    
    # Get farmer names for each listing
    for l in listings:
        farmer = await get_user(db, l.get("farmerId"))
        l["farmerName"] = farmer.get("name") if farmer else "Unknown"
    
    # Filter out buyer's own listings
    if buyer_id:
        listings = [l for l in listings if l.get("farmerId") != buyer_id]
    
    # Sort by price ascending (cheapest first)
    listings.sort(key=lambda x: x.get("priceConfirmed") or x.get("priceSuggested") or 999999)
    return listings[:5]  # Return top 5


def format_match_list(listings: list, language: str = "en") -> str:
    if not language:
        language = "en"

    if not listings:
        msgs = {
            "en": "No farmers found right now for that product.",
            "fr": "Aucun agriculteur trouvé pour ce produit.",
            "pidgin": "No farmer dey sell dat one now.",
        }
        return msgs.get(language, msgs["en"])

    lines = []
    for i, l in enumerate(listings, 1):
        price = l.get("priceConfirmed") or l.get("priceSuggested") or "?"
        qty = l.get("quantity", "?")
        loc = l.get("location", "?")
        unit = l.get("unit", "bags")
        farmer_name = l.get("farmerName", "Unknown")
        price_str = f"{int(price):,}".replace(",", " ") if isinstance(price, (int, float)) else str(price)
        lines.append(f"{i}. 👨‍🌾 {farmer_name} — 📍 {loc}\n   {qty} {unit} @ {price_str} FCFA")

    return "\n".join(lines)
