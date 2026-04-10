import nest_asyncio
import asyncio
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from src.config import settings
from src.handlers.dispatcher import dispatch_message, dispatch_callback, dispatch_voice
from src.database import close_connections

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

nest_asyncio.apply()


def build_app() -> Application:
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", dispatch_message))
    app.add_handler(CommandHandler("help",  dispatch_message))
    app.add_handler(CommandHandler("menu",  dispatch_message))

    # Text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, dispatch_message))

    # Voice messages
    app.add_handler(MessageHandler(filters.VOICE, dispatch_voice))

    # Inline keyboard callbacks
    app.add_handler(CallbackQueryHandler(dispatch_callback))

    return app


async def post_init(app: Application):
    await app.bot.set_my_commands([
        ("start", "Start / Restart AgroLink"),
        ("menu",  "Go to main menu"),
        ("help",  "How to use AgroLink"),
    ])
    logger.info(f"✅ {settings.BOT_NAME} bot is running!")


async def main():
    app = build_app()
    app.post_init = post_init

    logger.info("Starting AgroLink Telegram bot in polling mode...")
    await app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped.")
    finally:
        asyncio.run(close_connections())
