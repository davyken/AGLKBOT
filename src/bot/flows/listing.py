from telegram import Bot
from src.bot.conversation import State, update_state, get_session, set_session
from src.bot.messages import msg
from src.bot.keyboards import price_choice_keyboard, farmer_menu_keyboard, menu_button
from src.bot.human_typing import send_typing_then_message, send_quick
from src.services.price_engine import suggest_price, format_price
from src.models.models import create_listing, confirm_listing_price


async def start_listing(bot: Bot, chat_id: int, telegram_id: int, sessions_coll, db):
    """Farmer taps 'List produce' — ask what product."""
    session = await get_session(sessions_coll, telegram_id)
    lang = session["data"].get("language", "en")
    await update_state(sessions_coll, telegram_id, State.LIST_PRODUCT)
    await send_typing_then_message(bot, chat_id, msg("ask_product", lang))


async def handle_list_product(bot: Bot, chat_id: int, telegram_id: int, product: str, sessions_coll, db):
    """Store product, ask quantity."""
    session = await get_session(sessions_coll, telegram_id)
    lang = session["data"].get("language", "en")

    price_data = suggest_price(product)
    unit = price_data["unit"] if price_data else "bags"

    await update_state(sessions_coll, telegram_id, State.LIST_QUANTITY, {"list_product": product.lower(), "list_unit": unit})
    await send_typing_then_message(
        bot, chat_id,
        msg("ask_quantity", lang, product=product, unit=unit),
    )


async def handle_list_quantity(bot: Bot, chat_id: int, telegram_id: int, quantity: int, sessions_coll, db):
    """Store quantity, show price suggestion."""
    session = await get_session(sessions_coll, telegram_id)
    lang = session["data"].get("language", "en")
    product = session["data"].get("list_product", "")
    unit = session["data"].get("list_unit", "bags")

    price_data = suggest_price(product)

    await update_state(sessions_coll, telegram_id, State.LIST_PRICE_CHOICE, {"list_quantity": quantity})

    if price_data:
        suggested_str = format_price(price_data["suggested"])
        await send_typing_then_message(
            bot, chat_id,
            msg(
                "price_suggestion", lang,
                product=product,
                min=format_price(price_data["min"]),
                avg=format_price(price_data["avg"]),
                max=format_price(price_data["max"]),
                suggested=suggested_str,
            ),
            reply_markup=price_choice_keyboard(lang, suggested_str),
        )
        # Store suggested price for auto-selection
        await update_state(sessions_coll, telegram_id, None, {"list_price_suggested": price_data["suggested"]})
    else:
        await send_typing_then_message(
            bot, chat_id,
            msg("no_price_data", lang, product=product),
        )
        await update_state(sessions_coll, telegram_id, State.LIST_PRICE_MANUAL)


async def handle_price_auto(bot: Bot, chat_id: int, telegram_id: int, sessions_coll, db):
    """Farmer chose suggested price — confirm listing."""
    session = await get_session(sessions_coll, telegram_id)
    lang = session["data"].get("language", "en")
    data = session["data"]
    price = data.get("list_price_suggested", 0)
    await _confirm_listing(bot, chat_id, telegram_id, price, session, lang, sessions_coll, db)


async def handle_price_manual(bot: Bot, chat_id: int, telegram_id: int, sessions_coll, db):
    """Farmer wants to enter own price — ask for it."""
    session = await get_session(sessions_coll, telegram_id)
    lang = session["data"].get("language", "en")
    await update_state(sessions_coll, telegram_id, State.LIST_PRICE_MANUAL)
    await send_quick(bot, chat_id, "💬 " + {
        "en": "Enter your price (numbers only, e.g. *21000*):",
        "fr": "Entrez votre prix (chiffres uniquement, ex: *21000*) :",
        "pidgin": "Put your price (number only, e.g. *21000*):",
    }.get(lang, "Enter your price:"))


async def handle_price_manual_input(bot: Bot, chat_id: int, telegram_id: int, price_text: str, sessions_coll, db):
    """Parse and confirm manually entered price."""
    session = await get_session(sessions_coll, telegram_id)
    lang = session["data"].get("language", "en")

    clean = price_text.replace(",", "").replace(" ", "").replace("fcfa", "").replace("FCFA", "")
    try:
        price = float(clean)
    except ValueError:
        await send_quick(bot, chat_id, msg("invalid_price", lang))
        return

    await _confirm_listing(bot, chat_id, telegram_id, price, session, lang, sessions_coll, db)


async def _confirm_listing(bot: Bot, chat_id: int, telegram_id: int, price: float, session: dict, lang: str, sessions_coll, db):
    """Save listing to DB and notify farmer."""
    data = session["data"]
    name = data.get("name", "")
    product = data.get("list_product", "")
    quantity = data.get("list_quantity", 0)
    unit = data.get("list_unit", "bags")
    location = data.get("location", "")

    listing = await create_listing(db, telegram_id, {
        "product": product,
        "quantity": quantity,
        "unit": unit,
        "priceSuggested": price,
        "priceConfirmed": price,
        "location": location,
    })

    await update_state(sessions_coll, telegram_id, State.FARMER_MENU, {"last_listing_id": str(listing["_id"])})

    await send_typing_then_message(
        bot, chat_id,
        msg(
            "listing_confirmed", lang,
            name=name,
            product=product.title(),
            quantity=quantity,
            unit=unit,
            price=format_price(price),
        ),
        reply_markup=farmer_menu_keyboard(lang),
    )
