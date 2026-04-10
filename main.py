import asyncio
import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from src.config import settings
from src.handlers.dispatcher import dispatch_message, dispatch_callback, dispatch_voice
from src.database import get_db, close_connections

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─── Health-check server (Render requires an open port) ───────────────────
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, *args):
        pass

def start_health_server():
    port = int(os.environ.get("PORT", 8000))
    HTTPServer(("0.0.0.0", port), HealthCheck).serve_forever()


# ─── App builder ──────────────────────────────────────────────────────────
def build_app() -> Application:
    app = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)   # ← async init goes here, not in main()
        .build()
    )

    app.add_handler(CommandHandler("start", dispatch_message))
    app.add_handler(CommandHandler("help",  dispatch_message))
    app.add_handler(CommandHandler("menu",  dispatch_message))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, dispatch_message))
    app.add_handler(MessageHandler(filters.VOICE, dispatch_voice))
    app.add_handler(CallbackQueryHandler(dispatch_callback))

    return app


# ─── post_init: runs inside PTB's own event loop ──────────────────────────
async def post_init(app: Application):
    await app.bot.set_my_commands([
        ("start", "Start / Restart AgroLink"),
        ("menu",  "Go to main menu"),
        ("help",  "How to use AgroLink"),
    ])
    logger.info(f"✅ {settings.BOT_NAME} bot is running!")


# ─── Synchronous entry point ──────────────────────────────────────────────
def main():
    threading.Thread(target=start_health_server, daemon=True).start()

    # Python 3.10+ no longer auto-creates an event loop — set one explicitly
    asyncio.set_event_loop(asyncio.new_event_loop())

    app = build_app()

    logger.info("Starting AgroLink Telegram bot in polling mode...")
    app.run_polling(drop_pending_updates=True)   # synchronous, no await


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
    except KeyboardInterrupt:
        logger.info("Bot stopped.")
    finally:
        close_connections()