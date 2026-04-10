from telegram import Bot
from src.bot.conversation import State, update_state, get_session, set_session
from src.bot.messages import msg
from src.bot.keyboards import role_keyboard, farmer_menu_keyboard, buyer_menu_keyboard, language_keyboard
from src.bot.human_typing import send_typing_then_message, send_quick
from src.models.models import create_user, get_user
from src.config import settings
import httpx


async def register_user_to_backend(telegram_id: int, data: dict) -> dict | None:
    """Register user to the backend API."""
    backend_url = getattr(settings, 'BACKEND_URL', None)
    if not backend_url:
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{backend_url}/users/register",
                json={
                    "telegramId": str(telegram_id),
                    "name": data.get("name"),
                    "role": data.get("role"),
                    "location": data.get("location", "Unknown"),
                    "produces": data.get("produces", []),
                    "businessName": data.get("businessName"),
                    "needs": data.get("needs", []),
                    "language": data.get("language", "en"),
                },
                timeout=10.0,
            )
            if response.status_code == 201:
                return response.json().get("data")
    except Exception as e:
        print(f"Backend registration failed: {e}")
    return None


async def handle_start(bot: Bot, chat_id: int, telegram_id: int, username: str, sessions_coll, db):
    """Handle /start command — show language selector."""
    await update_state(sessions_coll, telegram_id, State.CHOOSE_LANGUAGE, {"username": username or ""})
    await send_typing_then_message(
        bot, chat_id,
        "🌍 Choose your language / Choisissez votre langue / Choose your language:",
        reply_markup=language_keyboard(),
    )


async def handle_language_chosen(bot: Bot, chat_id: int, telegram_id: int, lang: str, sessions_coll, db):
    """User picked a language — show role selection."""
    await update_state(sessions_coll, telegram_id, State.CHOOSE_ROLE, {"language": lang})
    await send_typing_then_message(
        bot, chat_id,
        msg("welcome", lang),
        reply_markup=role_keyboard(lang),
    )


async def handle_role_chosen(bot: Bot, chat_id: int, telegram_id: int, role: str, sessions_coll, db):
    """User picked farmer or buyer — ask for name."""
    session = await get_session(sessions_coll, telegram_id)
    lang = session["data"].get("language", "en")
    await update_state(sessions_coll, telegram_id, State.REG_NAME, {"role": role})
    await send_typing_then_message(bot, chat_id, msg("ask_name", lang))


async def handle_reg_name(bot: Bot, chat_id: int, telegram_id: int, name: str, sessions_coll, db):
    """Store name, ask location."""
    session = await get_session(sessions_coll, telegram_id)
    lang = session["data"].get("language", "en")
    await update_state(sessions_coll, telegram_id, State.REG_LOCATION, {"name": name.strip()})
    await send_typing_then_message(
        bot, chat_id,
        msg("ask_location", lang, name=name.strip()),
    )


async def handle_reg_location(bot: Bot, chat_id: int, telegram_id: int, location: str, sessions_coll, db):
    """Store location — branch to farmer (ask produces) or buyer (ask business name)."""
    session = await get_session(sessions_coll, telegram_id)
    lang = session["data"].get("language", "en")
    name = session["data"].get("name", "")
    role = session["data"].get("role", "farmer")

    await update_state(sessions_coll, telegram_id, None, {"location": location.strip()})

    # Reload session to get merged data with location
    session = await get_session(sessions_coll, telegram_id)
    lang = session["data"].get("language", "en")

    if role == "farmer":
        session["state"] = State.REG_PRODUCES
        await set_session(sessions_coll, telegram_id, session)
        await send_typing_then_message(
            bot, chat_id,
            msg("ask_produces", lang, name=name, location=location.strip()),
        )
    else:
        session["state"] = State.REG_BUSINESS_NAME
        await set_session(sessions_coll, telegram_id, session)
        await send_typing_then_message(bot, chat_id, msg("ask_business_name", lang))


async def handle_reg_produces(bot: Bot, chat_id: int, telegram_id: int, produces_text: str, sessions_coll, db):
    """Store produces list, complete farmer registration."""
    session = await get_session(sessions_coll, telegram_id)
    lang = session["data"].get("language", "en")
    data = session["data"]

    produces = [p.strip() for p in produces_text.replace(",", " ").split() if p.strip()]

    # Save to MongoDB (local)
    user = await create_user(db, telegram_id, {
        "role": "farmer",
        "name": data["name"],
        "location": data.get("location", "Unknown"),
        "produces": produces,
        "language": lang,
        "username": data.get("username", ""),
    })

    # Register to backend
    await register_user_to_backend(telegram_id, {
        "role": "farmer",
        "name": data["name"],
        "location": data.get("location", "Unknown"),
        "produces": produces,
        "language": lang,
    })

    await update_state(sessions_coll, telegram_id, State.FARMER_MENU, {"userId": str(user["_id"])})

    await send_typing_then_message(
        bot, chat_id,
        msg("registration_complete_farmer", lang, name=data["name"], location=data.get("location", "Unknown")),
        reply_markup=farmer_menu_keyboard(lang),
    )


async def handle_reg_business_name(bot: Bot, chat_id: int, telegram_id: int, business_name: str, sessions_coll, db):
    """Store business name, complete buyer registration."""
    session = await get_session(sessions_coll, telegram_id)
    lang = session["data"].get("language", "en")
    data = session["data"]

    user = await create_user(db, telegram_id, {
        "role": "buyer",
        "name": business_name.strip(),
        "location": data.get("location", "Unknown"),
        "language": lang,
        "username": data.get("username", ""),
    })

    # Register to backend
    await register_user_to_backend(telegram_id, {
        "role": "buyer",
        "name": business_name.strip(),
        "location": data.get("location", "Unknown"),
        "businessName": business_name.strip(),
        "language": lang,
    })

    await update_state(sessions_coll, telegram_id, State.BUYER_MENU, {
        "userId": str(user["_id"]),
        "name": business_name.strip(),
    })

    await send_typing_then_message(
        bot, chat_id,
        msg("registration_complete_buyer", lang, name=business_name.strip(), location=data.get("location", "Unknown")),
        reply_markup=buyer_menu_keyboard(lang),
    )
