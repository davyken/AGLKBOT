# AgroLink Telegram Bot

Telegram bot connecting farmers with buyers across Cameroon.

## Tech Stack

- Python 3.11.9
- python-telegram-bot==21.10
- openai==1.30.1 (GPT-4o-mini for intent parsing, Whisper-1 for voice transcription)
- motor==3.6.0 (MongoDB async driver)
- redis==5.0.4
- pydantic-settings==2.3.0

## Architecture

```
main.py                 # Entry point, bot initialization, health-check server
src/
  config.py             # Settings via pydantic (env vars)
  database.py           # MongoDB connection management
  models/models.py      # User, listing, request, match CRUD
  handlers/dispatcher.py  # Message, callback, voice dispatchers
  bot/
    conversation.py    # State machine and session management
    messages.py         # Localized messages (en/fr/pidgin)
    keyboards.py       # Inline keyboards
    human_typing.py     # Typing indicator helpers
    flows/
      register.py      # Registration flow (language -> role -> name -> location -> produces)
      listing.py       # Farmer listing flow (product -> quantity -> price)
      buyer.py         # Buyer request flow (product -> quantity -> match)
    services/
      ai.py            # OpenAI wrappers (intent parsing, voice transcription, replies)
      price_engine.py # Market price suggestions
      match_engine.py # Farmer-buyer matching
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token from @BotFather |
| `OPENAI_API_KEY` | Yes | OpenAI API key for intent parsing and voice |
| `MONGODB_URI` | Yes | MongoDB connection string |
| `OPENAI_MODEL` | No | Model for intent parsing (default: gpt-4o-mini) |
| `OPENAI_WHISPER_MODEL` | No | Model for voice transcription (default: whisper-1) |
| `BOT_NAME` | No | Bot display name (default: Amara) |
| `BACKEND_URL` | No | External backend for user sync |
| `PORT` | No | Health-check server port (default: 8000) |

## Local Setup

1. Create `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your_token
   OPENAI_API_KEY=your_key
   MONGODB_URI=mongodb://localhost:27017
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the bot:
   ```
   python main.py
   ```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start/restart the bot, triggers language selection |
| `/menu` | Show main menu (farmer or buyer actions) |
| `/help` | Show usage instructions |

### Menu Actions (inline buttons)

**Farmers:**
- `List produce` - Create a new listing
- `My listings` - View active listings
- `Menu` / `Help`

**Buyers:**
- `Request produce` - Search for farmers with matching product
- `Browse` - Browse active listings
- `Menu` / `Help`

### Natural Language Shortcuts

Farmers: `SELL maize 10 bags` - Auto-fills product and quantity
Buyers: `BUY tomatoes 5 crates` - Auto-fills product and quantity

## Deployment

### Render (recommended)

1. Connect repo to Render
2. Build command: `pip install -r requirements.txt`
3. Start command: `python main.py`
4. Set environment variables in Render dashboard
5. Health-check endpoint: `GET /` returns `OK` on the configured PORT

### Vercel (via `vercel-python`)

1. Add `vercel.json` with python-telegram-bot worker configuration
2. Set environment variables in Vercel dashboard
3. Deploy as serverless function with polling disabled (use webhook instead - not implemented)

## Known Limitations

- No webhook support - runs in long-polling mode only
- No admin panel - user management via MongoDB directly
- No transaction system - deals are manual (contact exchange only)
- Price data is hardcoded seed data, not fetched from live market API
- No retry logic for failed backend sync calls
- Sessions use MongoDB TTL (not Redis), causing connection overhead per request