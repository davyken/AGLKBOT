"""
All bot messages in 3 languages.
Usage: msg("welcome", lang)
"""

MESSAGES = {
    # ── Welcome ───────────────────────────────────────
    "welcome": {
        "en": (
            "👋 Hello! I'm *Amara*, your AgroLink assistant.\n\n"
            "I connect farmers with buyers across Cameroon — quickly and easily.\n\n"
            "Are you a *Farmer* or a *Buyer*?"
        ),
        "fr": (
            "👋 Bonjour ! Je suis *Amara*, votre assistante AgroLink.\n\n"
            "Je connecte les agriculteurs avec les acheteurs à travers le Cameroun.\n\n"
            "Êtes-vous un *Agriculteur* ou un *Acheteur* ?"
        ),
        "pidgin": (
            "👋 How now! I be *Amara*, your AgroLink helper.\n\n"
            "I dey connect farmers with buyers for whole Cameroon — e easy!\n\n"
            "You be *Farmer* or *Buyer*?"
        ),
    },

    # ── Language select ───────────────────────────────
    "choose_language": {
        "en": "Which language do you prefer? 🌍",
        "fr": "Quelle langue préférez-vous ? 🌍",
        "pidgin": "Which language you like? 🌍",
    },

    # ── Registration ──────────────────────────────────
    "ask_name": {
        "en": "Great choice! 😊 What's your full name?",
        "fr": "Excellent ! 😊 Quel est votre nom complet ?",
        "pidgin": "Fine! 😊 Wetin be your full name?",
    },
    "ask_location": {
        "en": "Nice to meet you, {name}! 🤝\n\nWhich city or region are you based in?",
        "fr": "Ravi de vous rencontrer, {name} ! 🤝\n\nDans quelle ville ou région êtes-vous ?",
        "pidgin": "How you dey, {name}! 🤝\n\nWhich town or region you dey stay?",
    },
    "ask_produces": {
        "en": "Perfect, {name} from {location}! 🌱\n\nWhat do you grow? (e.g. maize, tomatoes, plantain)\n\nYou can list several things.",
        "fr": "Parfait, {name} de {location} ! 🌱\n\nQue cultivez-vous ? (ex: maïs, tomates, plantains)\n\nVous pouvez lister plusieurs produits.",
        "pidgin": "Fine fine, {name} from {location}! 🌱\n\nWetin you dey grow? (e.g. maize, tomatoes, plantain)\n\nYou fit list plenty things.",
    },
    "registration_complete_farmer": {
        "en": (
            "✅ Welcome to AgroLink, *{name}*!\n\n"
            "You're registered as a farmer in *{location}*.\n"
            "You can start listing your produce right now 🌽"
        ),
        "fr": (
            "✅ Bienvenue sur AgroLink, *{name}* !\n\n"
            "Vous êtes inscrit comme agriculteur à *{location}*.\n"
            "Vous pouvez commencer à lister vos produits 🌽"
        ),
        "pidgin": (
            "✅ Welcome for AgroLink, *{name}*!\n\n"
            "You register as farmer for *{location}*.\n"
            "You fit start sell your thing now 🌽"
        ),
    },
    "ask_business_name": {
        "en": "Great! What's your business name?",
        "fr": "Super ! Quel est le nom de votre entreprise ?",
        "pidgin": "Fine! Wetin be your business name?",
    },
    "registration_complete_buyer": {
        "en": (
            "✅ Welcome to AgroLink, *{name}*!\n\n"
            "You're registered as a buyer in *{location}*.\n"
            "You can now search for fresh produce 🛒"
        ),
        "fr": (
            "✅ Bienvenue sur AgroLink, *{name}* !\n\n"
            "Vous êtes inscrit comme acheteur à *{location}*.\n"
            "Vous pouvez maintenant rechercher des produits frais 🛒"
        ),
        "pidgin": (
            "✅ Welcome for AgroLink, *{name}*!\n\n"
            "You register as buyer for *{location}*.\n"
            "You fit start find fresh things 🛒"
        ),
    },

    # ── Main menus ────────────────────────────────────
    "farmer_menu": {
        "en": "What would you like to do today, {name}? 👇",
        "fr": "Que souhaitez-vous faire aujourd'hui, {name} ? 👇",
        "pidgin": "Wetin you wan do today, {name}? 👇",
    },
    "buyer_menu": {
        "en": "What would you like to do today, {name}? 👇",
        "fr": "Que souhaitez-vous faire aujourd'hui, {name} ? 👇",
        "pidgin": "Wetin you wan do today, {name}? 👇",
    },

    # ── Listing flow ──────────────────────────────────
    "ask_product": {
        "en": "What product are you selling? 🌾",
        "fr": "Quel produit vendez-vous ? 🌾",
        "pidgin": "Wetin you wan sell? 🌾",
    },
    "ask_quantity": {
        "en": "How many {unit} of {product} do you have?",
        "fr": "Combien de {unit} de {product} avez-vous ?",
        "pidgin": "How many {unit} of {product} you get?",
    },
    "price_suggestion": {
        "en": (
            "📊 *{product} prices today:*\n\n"
            "▪️ Min:  {min}\n"
            "▪️ Avg:  {avg}\n"
            "▪️ Max:  {max}\n\n"
            "💡 My suggestion: *{suggested}*\n\n"
            "What price do you want to set?"
        ),
        "fr": (
            "📊 *Prix du {product} aujourd'hui :*\n\n"
            "▪️ Min :  {min}\n"
            "▪️ Moy : {avg}\n"
            "▪️ Max : {max}\n\n"
            "💡 Ma suggestion : *{suggested}*\n\n"
            "Quel prix voulez-vous fixer ?"
        ),
        "pidgin": (
            "📊 *{product} price today:*\n\n"
            "▪️ Min:  {min}\n"
            "▪️ Avg:  {avg}\n"
            "▪️ Max:  {max}\n\n"
            "💡 I suggest: *{suggested}*\n\n"
            "Which price you wan set?"
        ),
    },
    "no_price_data": {
        "en": "I don't have market data for {product} yet 😕\n\nWhat price would you like to set?",
        "fr": "Je n'ai pas encore de données de marché pour {product} 😕\n\nQuel prix souhaitez-vous fixer ?",
        "pidgin": "I no get price data for {product} yet 😕\n\nWhich price you wan give am?",
    },
    "listing_confirmed": {
        "en": (
            "🎉 Your listing is live, {name}!\n\n"
            "📦 *{product}* — {quantity} {unit} @ *{price}*\n\n"
            "Buyers in your area will be notified. I'll let you know when someone is interested! 🔔"
        ),
        "fr": (
            "🎉 Votre annonce est en ligne, {name} !\n\n"
            "📦 *{product}* — {quantity} {unit} @ *{price}*\n\n"
            "Les acheteurs de votre région seront notifiés. Je vous préviendrai dès qu'un acheteur sera intéressé ! 🔔"
        ),
        "pidgin": (
            "🎉 Your thing don list, {name}!\n\n"
            "📦 *{product}* — {quantity} {unit} @ *{price}*\n\n"
            "Buyers near you go receive notification. I go tell you when somebody interested! 🔔"
        ),
    },

    # ── Buyer flow ────────────────────────────────────
    "ask_product_buy": {
        "en": "What product are you looking for? 🛒",
        "fr": "Quel produit recherchez-vous ? 🛒",
        "pidgin": "Wetin you dey find? 🛒",
    },
    "ask_quantity_buy": {
        "en": "How many {unit} of {product} do you need?",
        "fr": "Combien de {unit} de {product} vous faut-il ?",
        "pidgin": "How many {unit} of {product} you need?",
    },
    "matches_found": {
        "en": "✅ Found *{count}* farmer(s) near you with *{product}*:\n\n{list}\n\nTap a number to connect 👇",
        "fr": "✅ Trouvé *{count}* agriculteur(s) près de vous avec *{product}* :\n\n{list}\n\nAppuyez sur un numéro pour vous connecter 👇",
        "pidgin": "✅ I find *{count}* farmer(s) near you with *{product}*:\n\n{list}\n\nPress number to connect 👇",
    },
    "no_matches": {
        "en": "😕 No farmers found for *{product}* right now.\n\nDon't worry — I'll notify you as soon as one becomes available! 🔔",
        "fr": "😕 Aucun agriculteur trouvé pour *{product}* pour le moment.\n\nNe vous inquiétez pas — je vous notifierai dès qu'un agriculteur sera disponible ! 🔔",
        "pidgin": "😕 No farmer get *{product}* now.\n\nNo worry — I go tell you as soon as one dey! 🔔",
    },
    "connection_request_sent": {
        "en": "⏳ Request sent to the farmer! Waiting for their reply...\n\nI'll notify you right away when they respond.",
        "fr": "⏳ Demande envoyée à l'agriculteur ! En attente de sa réponse...\n\nJe vous notifierai dès qu'il répondra.",
        "pidgin": "⏳ I don send request to the farmer! Dey wait for their answer...\n\nI go tell you quick quick when they reply.",
    },

    # ── Match notifications ───────────────────────────
    "farmer_match_request": {
        "en": (
            "🔔 Good news, {name}!\n\n"
            "📦 *{product}* ({quantity} {unit})\n"
            "👤 Buyer: {buyer_name}\n"
            "📞 Contact: {buyer_contact}\n"
            "📍 Location: {location}\n\n"
            "Are you interested?"
        ),
        "fr": (
            "🔔 Bonne nouvelle, {name} !\n\n"
            "📦 *{product}* ({quantity} {unit})\n"
            "👤 Acheteur: {buyer_name}\n"
            "📞 Contact: {buyer_contact}\n"
            "📍 Lieu: {location}\n\n"
            "Êtes-vous intéressé(e) ?"
        ),
        "pidgin": (
            "🔔 Good news, {name}!\n\n"
            "📦 *{product}* ({quantity} {unit})\n"
            "👤 Buyer: {buyer_name}\n"
            "📞 Contact: {buyer_contact}\n"
            "📍 Location: {location}\n\n"
            "You agree?"
        ),
    },
    "deal_accepted_farmer": {
        "en": (
            "🤝 Deal confirmed!\n\n"
            "Your buyer's contact:\n"
            "👤 *{buyer_name}*\n"
            "📱 @{buyer_username}\n\n"
            "You can chat directly now. Good luck! 🍀"
        ),
        "fr": (
            "🤝 Accord confirmé !\n\n"
            "Contact de votre acheteur :\n"
            "👤 *{buyer_name}*\n"
            "📱 @{buyer_username}\n\n"
            "Vous pouvez discuter directement maintenant. Bonne chance ! 🍀"
        ),
        "pidgin": (
            "🤝 Deal done!\n\n"
            "Your buyer contact:\n"
            "👤 *{buyer_name}*\n"
            "📱 @{buyer_username}\n\n"
            "Una fit talk direct now. Good luck! 🍀"
        ),
    },
    "deal_accepted_buyer": {
        "en": (
            "🤝 The farmer accepted!\n\n"
            "Your farmer's contact:\n"
            "👤 *{farmer_name}*\n"
            "📱 @{farmer_username}\n\n"
            "You can chat directly now. Enjoy! 🌽"
        ),
        "fr": (
            "🤝 L'agriculteur a accepté !\n\n"
            "Contact de votre agriculteur :\n"
            "👤 *{farmer_name}*\n"
            "📱 @{farmer_username}\n\n"
            "Vous pouvez discuter directement maintenant. Profitez-en ! 🌽"
        ),
        "pidgin": (
            "🤝 The farmer don agree!\n\n"
            "Your farmer contact:\n"
            "👤 *{farmer_name}*\n"
            "📱 @{farmer_username}\n\n"
            "Una fit talk direct now. Enjoy! 🌽"
        ),
    },
    "deal_rejected_buyer": {
        "en": "😔 The farmer is not available right now.\n\nLet me check if there are other options for you...",
        "fr": "😔 L'agriculteur n'est pas disponible en ce moment.\n\nLaissez-moi vérifier d'autres options pour vous...",
        "pidgin": "😔 The farmer no dey available now.\n\nLet me check other options for you...",
    },

    # ── Errors & fallbacks ────────────────────────────
    "not_understood": {
        "en": "Hmm, I didn't quite catch that 🤔\n\nCould you rephrase? For example:\n• *SELL maize 10 bags*\n• *BUY tomatoes 5 crates*",
        "fr": "Hmm, je n'ai pas bien compris 🤔\n\nPourriez-vous reformuler ? Par exemple :\n• *VENDRE maïs 10 sacs*\n• *ACHETER tomates 5 caisses*",
        "pidgin": "Hmm, I no understand well 🤔\n\nYou fit talk am again? For example:\n• *SELL maize 10 bags*\n• *BUY tomatoes 5 crates*",
    },
    "voice_received": {
        "en": "🎤 Got your voice message! Give me a second to listen...",
        "fr": "🎤 J'ai reçu votre message vocal ! Laissez-moi l'écouter...",
        "pidgin": "🎤 I don hear your voice message! Wait small...",
    },
    "voice_transcribed": {
        "en": "🎤 I heard: _{text}_",
        "fr": "🎤 J'ai entendu : _{text}_",
        "pidgin": "🎤 I hear say: _{text}_",
    },
    "voice_failed": {
        "en": "Sorry, I couldn't understand the audio 😕\n\nPlease try typing your message instead.",
        "fr": "Désolé, je n'ai pas pu comprendre l'audio 😕\n\nVeuillez essayer de taper votre message.",
        "pidgin": "Sorry, I no hear the audio well 😕\n\nPlease type your message.",
    },
    "error_generic": {
        "en": "Oops, something went wrong on my end 😅\n\nPlease try again!",
        "fr": "Oups, quelque chose s'est mal passé 😅\n\nVeuillez réessayer !",
        "pidgin": "Wahala! Something go wrong 😅\n\nPlease try again!",
    },
    "invalid_price": {
        "en": "That doesn't look like a valid price 🤔\n\nPlease enter a number (e.g. *21500*)",
        "fr": "Ce n'est pas un prix valide 🤔\n\nVeuillez entrer un nombre (ex: *21500*)",
        "pidgin": "That price no correct 🤔\n\nPlease put number (e.g. *21500*)",
    },
    "help": {
        "en": (
            "ℹ️ *How to use AgroLink:*\n\n"
            "🌾 *Farmers:* Type *SELL [product] [qty] bags* to list produce\n"
            "🛒 *Buyers:* Type *BUY [product] [qty] bags* to find sellers\n"
            "📊 *Prices:* Type *PRICE [product]* to check market rates\n\n"
            "Or just tap the menu buttons — I'll guide you! 😊"
        ),
        "fr": (
            "ℹ️ *Comment utiliser AgroLink :*\n\n"
            "🌾 *Agriculteurs :* Tapez *VENDRE [produit] [qté] sacs* pour lister\n"
            "🛒 *Acheteurs :* Tapez *ACHETER [produit] [qté] sacs* pour trouver\n"
            "📊 *Prix :* Tapez *PRIX [produit]* pour les tarifs du marché\n\n"
            "Ou appuyez sur les boutons du menu — je vous guiderai ! 😊"
        ),
        "pidgin": (
            "ℹ️ *How to use AgroLink:*\n\n"
            "🌾 *Farmers:* Type *SELL [product] [qty] bags* to sell\n"
            "🛒 *Buyers:* Type *BUY [product] [qty] bags* to find seller\n"
            "📊 *Price:* Type *PRICE [product]* to check market price\n\n"
            "Or just press the menu buttons — I go guide you! 😊"
        ),
    },
}


def msg(key: str, lang: str = "en", **kwargs) -> str:
    """Get a message template and format with kwargs."""
    lang = lang if lang in ["en", "fr", "pidgin"] else "en"
    template = MESSAGES.get(key, {}).get(lang) or MESSAGES.get(key, {}).get("en", "")
    try:
        return template.format(**kwargs)
    except KeyError:
        return template


# ── Inline keyboard labels ────────────────────────────

BUTTONS = {
    "farmer": {"en": "🌾 Farmer", "fr": "🌾 Agriculteur", "pidgin": "🌾 Farmer"},
    "buyer":  {"en": "🛒 Buyer",  "fr": "🛒 Acheteur",    "pidgin": "🛒 Buyer"},
    "list_produce":  {"en": "📦 List produce",   "fr": "📦 Lister des produits", "pidgin": "📦 List your thing"},
    "my_listings":   {"en": "📋 My listings",    "fr": "📋 Mes annonces",        "pidgin": "📋 My things"},
    "request_produce": {"en": "🔍 Request produce", "fr": "🔍 Chercher des produits", "pidgin": "🔍 Find something"},
    "browse":        {"en": "📖 Browse listings", "fr": "📖 Voir les annonces",   "pidgin": "📖 See listings"},
    "use_suggested": {"en": "✅ Use suggested",  "fr": "✅ Utiliser la suggestion", "pidgin": "✅ Use dat price"},
    "enter_own":     {"en": "✏️ Enter own price", "fr": "✏️ Entrer mon prix",    "pidgin": "✏️ Put my own price"},
    "yes":   {"en": "✅ Yes",  "fr": "✅ Oui",  "pidgin": "✅ Yes"},
    "no":    {"en": "❌ No",   "fr": "❌ Non",  "pidgin": "❌ No"},
    "menu":  {"en": "🏠 Menu", "fr": "🏠 Menu", "pidgin": "🏠 Menu"},
    "help":  {"en": "❓ Help", "fr": "❓ Aide", "pidgin": "❓ Help"},
    "lang_en":     {"en": "🇬🇧 English",  "fr": "🇬🇧 English",  "pidgin": "🇬🇧 English"},
    "lang_fr":     {"en": "🇫🇷 Français", "fr": "🇫🇷 Français", "pidgin": "🇫🇷 Français"},
    "lang_pidgin": {"en": "🇨🇲 Pidgin",   "fr": "🇨🇲 Pidgin",   "pidgin": "🇨🇲 Pidgin"},
}


def btn(key: str, lang: str = "en") -> str:
    lang = lang if lang in ["en", "fr", "pidgin"] else "en"
    return BUTTONS.get(key, {}).get(lang, key)
