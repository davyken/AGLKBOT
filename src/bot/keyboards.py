from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from src.bot.messages import btn


def inline(*rows: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    """
    Build InlineKeyboardMarkup.
    Each row is a list of (label, callback_data) tuples.
    Example: inline([("Yes", "yes"), ("No", "no")])
    """
    keyboard = []
    for row in rows:
        keyboard.append([InlineKeyboardButton(label, callback_data=cb) for label, cb in row])
    return InlineKeyboardMarkup(keyboard)


def role_keyboard(lang: str) -> InlineKeyboardMarkup:
    return inline(
        [(btn("farmer", lang), "role:farmer"), (btn("buyer", lang), "role:buyer")]
    )


def language_keyboard() -> InlineKeyboardMarkup:
    return inline(
        [(btn("lang_en"), "lang:en"), (btn("lang_fr"), "lang:fr"), (btn("lang_pidgin"), "lang:pidgin")]
    )


def farmer_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return inline(
        [(btn("list_produce", lang), "action:list"), (btn("my_listings", lang), "action:my_listings")],
        [(btn("help", lang), "action:help")],
    )


def buyer_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return inline(
        [(btn("request_produce", lang), "action:request"), (btn("browse", lang), "action:browse")],
        [(btn("help", lang), "action:help")],
    )


def price_choice_keyboard(lang: str, suggested: str) -> InlineKeyboardMarkup:
    return inline(
        [(f"✅ {suggested}", "price:auto")],
        [(btn("enter_own", lang), "price:manual")],
    )


def yes_no_keyboard(lang: str) -> InlineKeyboardMarkup:
    return inline(
        [(btn("yes", lang), "deal:yes"), (btn("no", lang), "deal:no")]
    )


def menu_button(lang: str) -> InlineKeyboardMarkup:
    return inline([(btn("menu", lang), "action:menu")])


def farmer_select_keyboard(listings: list, lang: str) -> InlineKeyboardMarkup:
    rows = []
    for i, listing in enumerate(listings, 1):
        loc = listing.get("location", "?")
        price = listing.get("priceConfirmed") or listing.get("priceSuggested") or "?"
        price_str = f"{int(price):,}".replace(",", " ") if isinstance(price, (int, float)) else str(price)
        rows.append([(f"{i}. {loc} — {price_str} FCFA", f"select_farmer:{i-1}")])
    rows.append([(btn("menu", lang), "action:menu")])
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data=cb) for label, cb in row] for row in rows])
