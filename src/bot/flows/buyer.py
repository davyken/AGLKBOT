from telegram import Bot
from src.bot.conversation import State, update_state, get_session, set_session
from src.bot.messages import msg
from src.bot.keyboards import buyer_menu_keyboard, farmer_select_keyboard, yes_no_keyboard, menu_button, farmer_menu_keyboard
from src.bot.human_typing import send_typing_then_message, send_quick
from src.services.match_engine import find_matches, format_match_list
from src.services.price_engine import suggest_price
from src.models.models import create_request, create_match, get_user


async def start_request(bot: Bot, chat_id: int, telegram_id: int, sessions_coll, db):
    """Buyer taps 'Request produce' — ask product."""
    session = await get_session(sessions_coll, telegram_id)
    lang = session["data"].get("language", "en")
    await update_state(sessions_coll, telegram_id, State.BUY_PRODUCT)
    await send_typing_then_message(bot, chat_id, msg("ask_product_buy", lang))


async def handle_buy_product(bot: Bot, chat_id: int, telegram_id: int, product: str, sessions_coll, db):
    """Store product, ask quantity."""
    session = await get_session(sessions_coll, telegram_id)
    lang = session["data"].get("language", "en")

    price_data = suggest_price(product)
    unit = price_data["unit"] if price_data else "bags"

    await update_state(sessions_coll, telegram_id, State.BUY_QUANTITY, {"buy_product": product.lower(), "buy_unit": unit})
    await send_typing_then_message(
        bot, chat_id,
        msg("ask_quantity_buy", lang, product=product, unit=unit),
    )


async def handle_buy_quantity(bot: Bot, chat_id: int, telegram_id: int, quantity: int, redis, db):
    """Store quantity, search for matches."""
    session = await get_session(redis, telegram_id)
    lang = session["data"].get("language", "en")
    data = session["data"]
    product = data.get("buy_product", "")
    unit = data.get("buy_unit", "bags")
    location = data.get("location", "")

    await update_state(redis, telegram_id, None, {"buy_quantity": quantity})

    # Show searching indicator
    await send_quick(bot, chat_id, {
        "en": "🔍 Searching for the best farmers...",
        "fr": "🔍 Recherche des meilleurs agricoles...",
        "pidgin": "🔍 I dey find best farmers for you...",
    }.get(lang, "🔍 Searching..."))

    listings = await find_matches(db, product, quantity, location, telegram_id)

    # Save request
    request = await create_request(db, telegram_id, {
        "product": product,
        "quantity": quantity,
        "location": location,
    })
    await update_state(redis, telegram_id, None, {"request_id": str(request["_id"])})

    if not listings:
        await send_typing_then_message(
            bot, chat_id,
            msg("no_matches", lang, product=product.title()),
            reply_markup=buyer_menu_keyboard(lang),
        )
        await update_state(redis, telegram_id, State.BUYER_MENU)
        return

    # Store listings in session for selection
    session = await get_session(redis, telegram_id)
    session["data"]["match_listings"] = [str(l["_id"]) for l in listings]
    session["data"]["match_farmer_ids"] = [l["farmerId"] for l in listings]
    session["state"] = State.BUY_SELECT_FARMER
    await set_session(redis, telegram_id, session)

    listing_text = format_match_list(listings, lang)
    await send_typing_then_message(
        bot, chat_id,
        msg("matches_found", lang,
            count=len(listings),
            product=product.title(),
            list=listing_text),
        reply_markup=farmer_select_keyboard(listings, lang),
    )


async def handle_farmer_selected(bot: Bot, chat_id: int, telegram_id: int, farmer_index: int, redis, db):
    """Buyer selected a farmer — send request to farmer."""
    session = await get_session(redis, telegram_id)
    lang = session["data"].get("language", "en")
    data = session["data"]

    farmer_ids = data.get("match_farmer_ids", [])
    listing_ids = data.get("match_listings", [])

    if farmer_index >= len(farmer_ids):
        await send_quick(bot, chat_id, msg("error_generic", lang))
        return

    farmer_telegram_id = farmer_ids[farmer_index]
    listing_id = listing_ids[farmer_index]
    request_id = data.get("request_id", "")
    product = data.get("buy_product", "")
    quantity = data.get("buy_quantity", 0)
    unit = data.get("buy_unit", "bags")
    buyer_location = data.get("location", "")

    # Create match record (pending)
    match = await create_match(db, listing_id, request_id, farmer_telegram_id, telegram_id)

    # Store match info in buyer session
    await update_state(redis, telegram_id, State.IDLE, {
        "pending_match_id": str(match["_id"]),
        "pending_farmer_id": farmer_telegram_id,
    })

    # Notify buyer
    await send_typing_then_message(
        bot, chat_id,
        msg("connection_request_sent", lang),
        reply_markup=menu_button(lang),
    )

    # Notify farmer
    farmer = await get_user(db, farmer_telegram_id)
    buyer = await get_user(db, telegram_id)
    if farmer:
        farmer_lang = farmer.get("language", "en")
        farmer_chat_id = farmer_telegram_id  # Telegram chat_id == user_id for private chats
        buyer_name = buyer.get("name", "") if buyer else ""
        buyer_username = buyer.get("username", "") if buyer else ""
        buyer_contact = f"@{buyer_username}" if buyer_username else f"ID: {telegram_id}"

        # Store pending deal in farmer's session
        from src.bot.conversation import get_session as gs, set_session as ss
        farmer_session = await gs(redis, farmer_telegram_id)
        farmer_session["state"] = State.FARMER_ACCEPT_DEAL
        farmer_session["data"]["pending_match_id"] = str(match["_id"])
        farmer_session["data"]["pending_buyer_id"] = telegram_id
        farmer_session["data"]["pending_buyer_name"] = buyer_name
        farmer_session["data"]["pending_buyer_contact"] = buyer_contact
        await ss(redis, farmer_telegram_id, farmer_session)

        await send_typing_then_message(
            bot, farmer_chat_id,
            msg(
                "farmer_match_request", farmer_lang,
                name=farmer.get("name", ""),
                buyer_name=buyer_name,
                buyer_contact=buyer_contact,
                location=buyer_location,
                product=product.title(),
                quantity=quantity,
                unit=unit,
            ),
            reply_markup=yes_no_keyboard(farmer_lang),
        )


async def handle_deal_response(bot: Bot, chat_id: int, telegram_id: int, accepted: bool, redis, db):
    """Farmer accepted or rejected a deal."""
    session = await get_session(redis, telegram_id)
    lang = session["data"].get("language", "en")
    data = session["data"]
    match_id = data.get("pending_match_id")
    buyer_id = data.get("pending_buyer_id")

    farmer = await get_user(db, telegram_id)
    farmer_name = farmer.get("name", "") if farmer else ""
    farmer_username = farmer.get("username", "") if farmer else ""

    # Update match status
    from src.models.models import update_match_status
    await update_match_status(db, match_id, "accepted" if accepted else "rejected")

    await update_state(redis, telegram_id, State.FARMER_MENU)

    if accepted:
        # Get buyer info
        buyer = await get_user(db, buyer_id)
        buyer_lang = buyer.get("language", "en") if buyer else "en"
        buyer_name = buyer.get("name", "") if buyer else ""
        buyer_username = buyer.get("username", "") if buyer else ""

        # Notify farmer
        await send_typing_then_message(
            bot, chat_id,
            msg("deal_accepted_farmer", lang,
                buyer_name=buyer_name,
                buyer_username=buyer_username or str(buyer_id)),
            reply_markup=farmer_menu_keyboard(lang),
        )

        # Notify buyer
        if buyer_id:
            await send_typing_then_message(
                bot, buyer_id,
                msg("deal_accepted_buyer", buyer_lang,
                    farmer_name=farmer_name,
                    farmer_username=farmer_username or str(telegram_id)),
            )
    else:
        # Notify farmer
        await send_typing_then_message(
            bot, chat_id,
            {
                "en": "No problem! I've let the buyer know. Ready for the next one? 💪",
                "fr": "Pas de problème ! J'ai informé l'acheteur. Prêt pour le prochain ? 💪",
                "pidgin": "No wahala! I don tell the buyer. You ready for next? 💪",
            }.get(lang, "Ok!"),
            reply_markup=farmer_menu_keyboard(lang),
        )
        # Notify buyer
        if buyer_id:
            buyer = await get_user(db, buyer_id)
            buyer_lang = buyer.get("language", "en") if buyer else "en"
            await send_typing_then_message(bot, buyer_id, msg("deal_rejected_buyer", buyer_lang))
