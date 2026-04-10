import json
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorCollection

SESSION_TTL = 60 * 30  # 30 minutes


# ── State constants ───────────────────────────────────

class State:
    # Onboarding
    START              = "start"
    CHOOSE_LANGUAGE    = "choose_language"
    CHOOSE_ROLE        = "choose_role"
    REG_NAME           = "reg_name"
    REG_LOCATION       = "reg_location"
    REG_PRODUCES       = "reg_produces"        # farmer only
    REG_BUSINESS_NAME  = "reg_business_name"   # buyer only

    # Farmer flows
    FARMER_MENU        = "farmer_menu"
    LIST_PRODUCT       = "list_product"
    LIST_QUANTITY      = "list_quantity"
    LIST_PRICE_CHOICE  = "list_price_choice"
    LIST_PRICE_MANUAL  = "list_price_manual"
    LIST_CONFIRM       = "list_confirm"

    # Buyer flows
    BUYER_MENU         = "buyer_menu"
    BUY_PRODUCT        = "buy_product"
    BUY_QUANTITY       = "buy_quantity"
    BUY_SELECT_FARMER  = "buy_select_farmer"

    # Match flow
    FARMER_ACCEPT_DEAL = "farmer_accept_deal"

    # Idle (registered, at menu)
    IDLE               = "idle"


async def get_session(sessions_coll: AsyncIOMotorCollection, telegram_id: int) -> dict:
    doc = await sessions_coll.find_one({"telegram_id": telegram_id})
    if doc and "session" in doc:
        return json.loads(doc["session"])
    return {"state": State.START, "data": {}}


async def set_session(sessions_coll: AsyncIOMotorCollection, telegram_id: int, session: dict):
    session_json = json.dumps(session)
    expires_at = datetime.utcnow() + timedelta(seconds=SESSION_TTL)
    await sessions_coll.replace_one(
        {"telegram_id": telegram_id},
        {"telegram_id": telegram_id, "session": session_json, "expiresAt": expires_at},
        upsert=True
    )


async def clear_session(sessions_coll: AsyncIOMotorCollection, telegram_id: int):
    await sessions_coll.delete_one({"telegram_id": telegram_id})


async def update_state(sessions_coll: AsyncIOMotorCollection, telegram_id: int, state: str, data: dict = None):
    session = await get_session(sessions_coll, telegram_id)
    session["state"] = state
    if data:
        session["data"].update(data)
    await set_session(sessions_coll, telegram_id, session)


async def get_state(sessions_coll: AsyncIOMotorCollection, telegram_id: int) -> str:
    session = await get_session(sessions_coll, telegram_id)
    return session.get("state", State.START)


async def get_data(sessions_coll: AsyncIOMotorCollection, telegram_id: int) -> dict:
    session = await get_session(sessions_coll, telegram_id)
    return session.get("data", {})
