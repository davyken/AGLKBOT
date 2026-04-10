from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from src.config import settings
import httpx


def now():
    return datetime.now(timezone.utc)


async def _get_backend_url() -> str | None:
    return getattr(settings, 'BACKEND_URL', None)


# ─── User ────────────────────────────────────────────

async def create_user(db, telegram_id: int, data: dict) -> dict:
    """Create user locally (upsert to prevent duplicates) AND register to backend."""
    # Check if user already exists
    existing = await db.users.find_one({"telegramId": telegram_id})
    if existing:
        # Update existing user
        await db.users.update_one(
            {"telegramId": telegram_id},
            {"$set": {
                "role": data.get("role"),
                "name": data.get("name"),
                "location": data.get("location"),
                "produces": data.get("produces", []),
                "language": data.get("language", "en"),
                "username": data.get("username"),
            }}
        )
        existing.update(data)
        user = existing
    else:
        # Create new user
        user = {
            "telegramId": telegram_id,
            "role": data.get("role"),
            "name": data.get("name"),
            "location": data.get("location"),
            "phone": data.get("phone"),  # May be None for Telegram
            "produces": data.get("produces", []),
            "language": data.get("language", "en"),
            "username": data.get("username"),
            "channel": "telegram",
            "createdAt": now(),
        }
        result = await db.users.insert_one(user)
        user["_id"] = result.inserted_id

    # Also register to backend
    backend_url = await _get_backend_url()
    if backend_url:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{backend_url}/users/register",
                    json={
                        "telegramId": str(telegram_id),
                        "phone": data.get("phone"),
                        "name": data.get("name"),
                        "role": data.get("role"),
                        "location": data.get("location", "Unknown"),
                        "produces": data.get("produces", []),
                        "language": data.get("language", "en"),
                    },
                    timeout=10.0,
                )
        except Exception as e:
            print(f"Backend registration failed: {e}")

    return user


async def get_user(db, telegram_id: int) -> Optional[dict]:
    """Get user from local DB, fallback to backend."""
    user = await db.users.find_one({"telegramId": telegram_id})
    
    # If not found locally, try backend
    if not user:
        backend_url = await _get_backend_url()
        if backend_url:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{backend_url}/users/telegram/{telegram_id}",
                        timeout=10.0,
                    )
                    if response.status_code == 200:
                        data = response.json().get("data")
                        if data:
                            # Convert backend user to local format
                            user = {
                                "telegramId": data.get("telegramId"),
                                "role": data.get("role"),
                                "name": data.get("name"),
                                "location": data.get("location"),
                                "produces": data.get("produces", []),
                                "language": data.get("language", "en"),
                                "channel": data.get("preferredChannel", "telegram"),
                            }
            except Exception as e:
                print(f"Backend user fetch failed: {e}")
    
    return user


async def update_user(db, telegram_id: int, data: dict):
    """Update user locally and sync to backend."""
    await db.users.update_one({"telegramId": telegram_id}, {"$set": data})

    # Sync to backend
    backend_url = await _get_backend_url()
    if backend_url:
        try:
            async with httpx.AsyncClient() as client:
                await client.put(
                    f"{backend_url}/users/telegram/{telegram_id}",
                    json=data,
                    timeout=10.0,
                )
        except Exception as e:
            print(f"Backend user update failed: {e}")


# ─── Listing ─────────────────────────────────────────

async def create_listing(db, farmer_id: int, data: dict) -> dict:
    listing = {
        "farmerId": farmer_id,
        "product": data["product"],
        "quantity": data["quantity"],
        "unit": data.get("unit", "bags"),
        "priceSuggested": data.get("priceSuggested"),
        "priceConfirmed": data.get("priceConfirmed"),
        "location": data.get("location"),
        "status": "active",
        "createdAt": now(),
    }
    result = await db.listings.insert_one(listing)
    listing["_id"] = result.inserted_id
    return listing


async def confirm_listing_price(db, listing_id: str, price: float):
    await db.listings.update_one(
        {"_id": ObjectId(listing_id)},
        {"$set": {"priceConfirmed": price, "status": "active"}},
    )


async def get_active_listings(db, product: str, location: str = None) -> list:
    query = {"product": {"$regex": product, "$options": "i"}, "status": "active"}
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    cursor = db.listings.find(query).limit(5)
    return await cursor.to_list(length=5)


# ─── Request ─────────────────────────────────────────

async def create_request(db, buyer_id: int, data: dict) -> dict:
    req = {
        "buyerId": buyer_id,
        "product": data["product"],
        "quantity": data["quantity"],
        "location": data.get("location"),
        "status": "open",
        "createdAt": now(),
    }
    result = await db.requests.insert_one(req)
    req["_id"] = result.inserted_id
    return req


# ─── Match ───────────────────────────────────────────

async def create_match(db, listing_id: str, request_id: str, farmer_id: int, buyer_id: int) -> dict:
    match = {
        "listingId": listing_id,
        "requestId": request_id,
        "farmerId": farmer_id,
        "buyerId": buyer_id,
        "status": "pending",
        "createdAt": now(),
    }
    result = await db.matches.insert_one(match)
    match["_id"] = result.inserted_id
    return match


async def update_match_status(db, match_id: str, status: str):
    await db.matches.update_one({"_id": ObjectId(match_id)}, {"$set": {"status": status}})


# ─── Prices seed data ────────────────────────────────

PRICE_DATA = {
    "maize":     {"min": 18000, "avg": 22000, "max": 26000, "unit": "bags"},
    "mais":      {"min": 18000, "avg": 22000, "max": 26000, "unit": "sacs"},
    "tomatoes":  {"min": 8000,  "avg": 12000, "max": 16000, "unit": "crates"},
    "tomates":   {"min": 8000,  "avg": 12000, "max": 16000, "unit": "caisses"},
    "plantain":  {"min": 5000,  "avg": 7500,  "max": 10000, "unit": "bunches"},
    "plantains": {"min": 5000,  "avg": 7500,  "max": 10000, "unit": "régimes"},
    "cassava":   {"min": 6000,  "avg": 9000,  "max": 12000, "unit": "bags"},
    "manioc":    {"min": 6000,  "avg": 9000,  "max": 12000, "unit": "sacs"},
    "yam":       {"min": 10000, "avg": 15000, "max": 20000, "unit": "bags"},
    "igname":    {"min": 10000, "avg": 15000, "max": 20000, "unit": "sacs"},
    "pepper":    {"min": 3000,  "avg": 5000,  "max": 8000,  "unit": "kg"},
    "piment":    {"min": 3000,  "avg": 5000,  "max": 8000,  "unit": "kg"},
}
