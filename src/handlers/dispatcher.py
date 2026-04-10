import httpx
from telegram import Update, Bot
from telegram.ext import ContextTypes

from src.bot.conversation import (
    State, get_session, get_state, update_state, get_data
)
from src.bot.messages import msg
from src.bot.keyboards import (
    farmer_menu_keyboard, buyer_menu_keyboard, language_keyboard, role_keyboard
)
from src.bot.human_typing import send_typing_then_message, send_quick
from src.bot.flows.register import (
    handle_start, handle_language_chosen, handle_role_chosen,
    handle_reg_name, handle_reg_location, handle_reg_produces,
    handle_reg_business_name,
)
from src.bot.flows.listing import (
    start_listing, handle_list_product, handle_list_quantity,
    handle_price_auto, handle_price_manual, handle_price_manual_input,
)
from src.bot.flows.buyer import (
    start_request, handle_buy_product, handle_buy_quantity,
    handle_farmer_selected, handle_deal_response,
)
from src.services.ai import parse_intent, detect_language, transcribe_voice, generate_reply
from src.models.models import get_user
from src.database import get_db, get_sessions_collection


# ─── Text message dispatcher ─────────────────────────

async def dispatch_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    bot: Bot = context.bot
    chat_id = message.chat_id
    telegram_id = message.from_user.id
    username = message.from_user.username or ""
    text = message.text or ""

    db = await get_db()
    sessions_coll = await get_sessions_collection(db)
    session = await get_session(sessions_coll, telegram_id)
    state = session.get("state", State.START)
    data = session.get("data", {})
    lang = data.get("language", "en")

    # ── /start command ────────────────────────────────
    if text.strip().startswith("/start"):
        await handle_start(bot, chat_id, telegram_id, username, sessions_coll, db)
        return

    # ── /help command ─────────────────────────────────
    if text.strip().startswith("/help"):
        await send_typing_then_message(bot, chat_id, msg("help", lang))
        return

    # ── /menu command ─────────────────────────────────
    if text.strip().startswith("/menu"):
        await _show_menu(bot, chat_id, telegram_id, sessions_coll, db)
        return

    # ── State-driven routing ──────────────────────────
    match state:

        case State.START | State.CHOOSE_LANGUAGE:
            # Detect language from first message and start
            detected = await detect_language(text)
            await handle_language_chosen(bot, chat_id, telegram_id, detected, sessions_coll, db)

        case State.CHOOSE_ROLE:
            parsed = await parse_intent(text)
            intent = parsed.get("intent", "unknown")
            if "farm" in text.lower() or intent == "sell":
                await handle_role_chosen(bot, chat_id, telegram_id, "farmer", sessions_coll, db)
            elif "buy" in text.lower() or intent == "buy":
                await handle_role_chosen(bot, chat_id, telegram_id, "buyer", sessions_coll, db)
            else:
                await send_quick(bot, chat_id, msg("not_understood", lang),
                                 reply_markup=role_keyboard(lang))

        case State.REG_NAME:
            await handle_reg_name(bot, chat_id, telegram_id, text, sessions_coll, db)

        case State.REG_LOCATION:
            await handle_reg_location(bot, chat_id, telegram_id, text, sessions_coll, db)

        case State.REG_PRODUCES:
            await handle_reg_produces(bot, chat_id, telegram_id, text, sessions_coll, db)

        case State.REG_BUSINESS_NAME:
            await handle_reg_business_name(bot, chat_id, telegram_id, text, sessions_coll, db)

        case State.LIST_PRODUCT:
            parsed = await parse_intent(text)
            product = parsed.get("product") or text.strip()
            await handle_list_product(bot, chat_id, telegram_id, product, sessions_coll, db)

        case State.LIST_QUANTITY:
            parsed = await parse_intent(text)
            qty = parsed.get("quantity")
            if qty:
                await handle_list_quantity(bot, chat_id, telegram_id, int(qty), sessions_coll, db)
            else:
                # Try to extract just a number
                import re
                nums = re.findall(r'\d+', text)
                if nums:
                    await handle_list_quantity(bot, chat_id, telegram_id, int(nums[0]), sessions_coll, db)
                else:
                    await send_quick(bot, chat_id, {
                        "en": "Please enter the quantity as a number (e.g. *10*)",
                        "fr": "Veuillez entrer la quantité en chiffres (ex: *10*)",
                        "pidgin": "Please put number for quantity (e.g. *10*)",
                    }.get(lang, "Enter a number:"))

        case State.LIST_PRICE_MANUAL:
            await handle_price_manual_input(bot, chat_id, telegram_id, text, sessions_coll, db)

        case State.BUY_PRODUCT:
            parsed = await parse_intent(text)
            product = parsed.get("product") or text.strip()
            await handle_buy_product(bot, chat_id, telegram_id, product, sessions_coll, db)

        case State.BUY_QUANTITY:
            parsed = await parse_intent(text)
            qty = parsed.get("quantity")
            if qty:
                await handle_buy_quantity(bot, chat_id, telegram_id, int(qty), sessions_coll, db)
            else:
                import re
                nums = re.findall(r'\d+', text)
                if nums:
                    await handle_buy_quantity(bot, chat_id, telegram_id, int(nums[0]), sessions_coll, db)
                else:
                    await send_quick(bot, chat_id, {
                        "en": "How many do you need? (enter a number)",
                        "fr": "Combien en voulez-vous ? (entrez un nombre)",
                        "pidgin": "How many you need? (put number)",
                    }.get(lang, "Enter quantity:"))

        case State.FARMER_ACCEPT_DEAL:
            parsed = await parse_intent(text)
            intent = parsed.get("intent", "unknown")
            if intent == "yes" or text.lower() in ["yes", "oui", "yes na", "i agree", "ok", "okay"]:
                await handle_deal_response(bot, chat_id, telegram_id, True, sessions_coll, db)
            elif intent == "no" or text.lower() in ["no", "non", "no be dat", "nope"]:
                await handle_deal_response(bot, chat_id, telegram_id, False, sessions_coll, db)
            else:
                await send_quick(bot, chat_id,
                    msg("not_understood", lang),
                    reply_markup=__import__('src.bot.keyboards', fromlist=['yes_no_keyboard']).yes_no_keyboard(lang))

        case State.FARMER_MENU | State.IDLE:
            # Intelligent free-text at farmer menu
            await _handle_freetext_farmer(bot, chat_id, telegram_id, text, lang, sessions_coll, db)

        case State.BUYER_MENU:
            await _handle_freetext_buyer(bot, chat_id, telegram_id, text, lang, sessions_coll, db)

        case _:
            await _handle_freetext_farmer(bot, chat_id, telegram_id, text, lang, sessions_coll, db)


# ─── Callback query dispatcher ────────────────────────

async def dispatch_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    bot: Bot = context.bot
    chat_id = query.message.chat_id
    telegram_id = query.from_user.id
    data_str = query.data or ""

    db = await get_db()
    sessions_coll = await get_sessions_collection(db)
    session = await get_session(sessions_coll, telegram_id)
    lang = session.get("data", {}).get("language", "en")

    if data_str.startswith("lang:"):
        lang_choice = data_str.split(":")[1]
        await handle_language_chosen(bot, chat_id, telegram_id, lang_choice, sessions_coll, db)

    elif data_str.startswith("role:"):
        role = data_str.split(":")[1]
        await handle_role_chosen(bot, chat_id, telegram_id, role, sessions_coll, db)

    elif data_str == "action:list":
        # Check if user is a farmer
        user = await get_user(db, telegram_id)
        if not user or user.get("role") != "farmer":
            await send_quick(bot, chat_id, {
                "en": "❌ Only farmers can list produce. You're registered as a buyer.",
                "fr": "❌ Seul les agricoles peuvent lister des produits. Vous êtes enregistré comme acheteur.",
                "pidgin": "❌ Only farmers fit list produce. You be buyer.",
            }.get(lang, "Only farmers can list produce."))
            return
        await start_listing(bot, chat_id, telegram_id, sessions_coll, db)

    elif data_str == "action:request":
        # Check if user is a buyer
        user = await get_user(db, telegram_id)
        if not user or user.get("role") != "buyer":
            await send_quick(bot, chat_id, {
                "en": "❌ Only buyers can request produce. You're registered as a farmer.",
                "fr": "❌ Seul les acheteurs peuvent demander des produits. Vous êtes enregistré comme agriculteur.",
                "pidgin": "❌ Only buyers fit request produce. You be farmer.",
            }.get(lang, "Only buyers can request produce."))
            return
        await start_request(bot, chat_id, telegram_id, sessions_coll, db)

    elif data_str == "action:menu":
        await _show_menu(bot, chat_id, telegram_id, sessions_coll, db)

    elif data_str == "action:help":
        await send_typing_then_message(bot, chat_id, msg("help", lang))

    elif data_str == "action:my_listings":
        await _show_my_listings(bot, chat_id, telegram_id, lang, sessions_coll, db)

    elif data_str == "action:browse":
        await start_request(bot, chat_id, telegram_id, sessions_coll, db)

    elif data_str == "price:auto":
        await handle_price_auto(bot, chat_id, telegram_id, sessions_coll, db)

    elif data_str == "price:manual":
        await handle_price_manual(bot, chat_id, telegram_id, sessions_coll, db)

    elif data_str.startswith("select_farmer:"):
        idx = int(data_str.split(":")[1])
        await handle_farmer_selected(bot, chat_id, telegram_id, idx, sessions_coll, db)

    elif data_str == "deal:yes":
        await handle_deal_response(bot, chat_id, telegram_id, True, sessions_coll, db)

    elif data_str == "deal:no":
        await handle_deal_response(bot, chat_id, telegram_id, False, sessions_coll, db)


# ─── Voice message handler ────────────────────────────

async def dispatch_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    bot: Bot = context.bot
    chat_id = message.chat_id
    telegram_id = message.from_user.id

    db = await get_db()
    sessions_coll = await get_sessions_collection(db)
    session = await get_session(sessions_coll, telegram_id)
    lang = session.get("data", {}).get("language", "en")

    # Acknowledge immediately
    await send_quick(bot, chat_id, msg("voice_received", lang))

    try:
        voice = message.voice
        file = await bot.get_file(voice.file_id)
        file_bytes = await file.download_as_bytearray()
        transcript = await transcribe_voice(bytes(file_bytes), "ogg")
    except Exception:
        await send_typing_then_message(bot, chat_id, msg("voice_failed", lang))
        return

    if not transcript:
        await send_typing_then_message(bot, chat_id, msg("voice_failed", lang))
        return

    # Show what was heard
    await send_quick(bot, chat_id, msg("voice_transcribed", lang, text=transcript))

    # Inject as a fake text message into the dispatcher
    update.message.text = transcript
    await dispatch_message(update, context)


# ─── Helpers ──────────────────────────────────────────

async def _show_menu(bot: Bot, chat_id: int, telegram_id: int, redis, db):
    session = await get_session(redis, telegram_id)
    lang = session.get("data", {}).get("language", "en")
    role = session.get("data", {}).get("role")
    name = session.get("data", {}).get("name", "")

    if not role:
        user = await get_user(db, telegram_id)
        if user:
            role = user.get("role")
            name = user.get("name", "")

    if role == "farmer":
        await update_state(redis, telegram_id, State.FARMER_MENU)
        await send_typing_then_message(
            bot, chat_id,
            msg("farmer_menu", lang, name=name),
            reply_markup=farmer_menu_keyboard(lang),
        )
    elif role == "buyer":
        await update_state(redis, telegram_id, State.BUYER_MENU)
        await send_typing_then_message(
            bot, chat_id,
            msg("buyer_menu", lang, name=name),
            reply_markup=buyer_menu_keyboard(lang),
        )
    else:
        await handle_start(bot, chat_id, telegram_id,
                           session.get("data", {}).get("username", ""), redis, db)


async def _handle_freetext_farmer(bot: Bot, chat_id: int, telegram_id: int, text: str, lang: str, redis, db):
    """Handle free text from a registered farmer."""
    # Double-check role
    user = await get_user(db, telegram_id)
    if not user or user.get("role") != "farmer":
        await send_quick(bot, chat_id, {
            "en": "❌ Only farmers can list produce.",
            "fr": "❌ Seul les agricoles peuvent lister.",
            "pidgin": "❌ Only farmers fit list.",
        }.get(lang, "Only farmers can list."))
        return
    
    parsed = await parse_intent(text)
    intent = parsed.get("intent", "unknown")
    product = parsed.get("product")
    quantity = parsed.get("quantity")

    if intent == "sell" and product and quantity:
        # Direct "SELL maize 10 bags" shortcut — fill both product and quantity
        await update_state(redis, telegram_id, State.LIST_QUANTITY, {
            "list_product": product,
            "list_unit": "bags",
        })
        await handle_list_quantity(bot, chat_id, telegram_id, int(quantity), redis, db)
    elif intent == "sell" and product:
        await update_state(redis, telegram_id, State.LIST_QUANTITY, {"list_product": product, "list_unit": "bags"})
        await send_typing_then_message(bot, chat_id, msg("ask_quantity", lang, product=product, unit="bags"))
    elif intent == "sell":
        await start_listing(bot, chat_id, telegram_id, redis, db)
    elif intent == "help":
        await send_typing_then_message(bot, chat_id, msg("help", lang))
    elif intent in ("greeting", "menu"):
        await _show_menu(bot, chat_id, telegram_id, redis, db)
    else:
        # Use GPT to generate a warm reply
        reply = await generate_reply(
            [{"role": "user", "content": text}],
            user_name=await _get_name(redis, db, telegram_id),
            language=lang,
        )
        await send_typing_then_message(
            bot, chat_id, reply,
            reply_markup=farmer_menu_keyboard(lang),
        )


async def _handle_freetext_buyer(bot: Bot, chat_id: int, telegram_id: int, text: str, lang: str, redis, db):
    """Handle free text from a registered buyer."""
    # Double-check role
    user = await get_user(db, telegram_id)
    if not user or user.get("role") != "buyer":
        await send_quick(bot, chat_id, {
            "en": "❌ Only buyers can request produce.",
            "fr": "❌ Seul les acheteurs peuvent demander.",
            "pidgin": "❌ Only buyers fit request.",
        }.get(lang, "Only buyers can request."))
        return
    
    parsed = await parse_intent(text)
    intent = parsed.get("intent", "unknown")
    product = parsed.get("product")
    quantity = parsed.get("quantity")

    if intent == "buy" and product and quantity:
        await update_state(redis, telegram_id, State.BUY_QUANTITY, {
            "buy_product": product, "buy_unit": "bags",
        })
        await handle_buy_quantity(bot, chat_id, telegram_id, int(quantity), redis, db)
    elif intent == "buy" and product:
        await update_state(redis, telegram_id, State.BUY_QUANTITY, {"buy_product": product, "buy_unit": "bags"})
        await send_typing_then_message(bot, chat_id, msg("ask_quantity_buy", lang, product=product, unit="bags"))
    elif intent == "buy":
        await start_request(bot, chat_id, telegram_id, redis, db)
    elif intent == "help":
        await send_typing_then_message(bot, chat_id, msg("help", lang))
    elif intent in ("greeting", "menu"):
        await _show_menu(bot, chat_id, telegram_id, redis, db)
    else:
        reply = await generate_reply(
            [{"role": "user", "content": text}],
            user_name=await _get_name(redis, db, telegram_id),
            language=lang,
        )
        await send_typing_then_message(
            bot, chat_id, reply,
            reply_markup=buyer_menu_keyboard(lang),
        )


async def _show_my_listings(bot: Bot, chat_id: int, telegram_id: int, lang: str, redis, db):
    """Show farmer's active listings."""
    cursor = db.listings.find({"farmerId": telegram_id, "status": "active"}).sort("createdAt", -1).limit(5)
    listings = await cursor.to_list(length=5)

    if not listings:
        await send_typing_then_message(bot, chat_id, {
            "en": "You have no active listings yet 📭\n\nTap *List produce* to add your first one!",
            "fr": "Vous n'avez pas encore d'annonces actives 📭\n\nAppuyez sur *Lister des produits* pour en ajouter une !",
            "pidgin": "You no get listing yet 📭\n\nPress *List produce* to add your first one!",
        }.get(lang, "No listings yet."), reply_markup=farmer_menu_keyboard(lang))
        return

    lines = []
    for l in listings:
        price = l.get("priceConfirmed") or l.get("priceSuggested") or "?"
        price_str = f"{int(price):,}".replace(",", " ") if isinstance(price, (int, float)) else str(price)
        lines.append(f"• {l['product'].title()} — {l['quantity']} {l.get('unit','bags')} @ {price_str} FCFA")

    header = {"en": "📦 *Your active listings:*", "fr": "📦 *Vos annonces actives :*", "pidgin": "📦 *Your listings:*"}.get(lang, "")
    await send_typing_then_message(
        bot, chat_id,
        header + "\n\n" + "\n".join(lines),
        reply_markup=farmer_menu_keyboard(lang),
    )


async def _get_name(redis, db, telegram_id: int) -> str | None:
    session = await get_session(redis, telegram_id)
    name = session.get("data", {}).get("name")
    if name:
        return name
    user = await get_user(db, telegram_id)
    return user.get("name") if user else None
