import asyncio
import math
from telegram import Bot
from telegram.constants import ChatAction


# Average human reading/typing speed constants
CHARS_PER_SECOND_READ = 20   # how fast bot "reads" incoming
CHARS_PER_SECOND_TYPE = 40   # how fast bot "types" reply
MIN_DELAY = 0.6
MAX_DELAY = 3.5
CHUNK_PAUSE = 0.8             # pause between message chunks


def _typing_delay(text: str) -> float:
    """Calculate realistic typing delay based on text length."""
    chars = len(text)
    delay = chars / CHARS_PER_SECOND_TYPE
    return min(max(delay, MIN_DELAY), MAX_DELAY)


def _split_into_chunks(text: str) -> list[str]:
    """
    Split long messages into natural chunks at paragraph breaks.
    Short messages stay as one chunk.
    """
    if len(text) < 180:
        return [text]
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if len(paragraphs) <= 1:
        return [text]
    return paragraphs


async def send_typing_then_message(
    bot: Bot,
    chat_id: int,
    text: str,
    reply_markup=None,
    parse_mode: str = "Markdown",
    split_chunks: bool = True,
):
    """
    Core human-like send function:
    1. Send typing action
    2. Wait realistic delay
    3. Send message
    For long messages, split into chunks with pauses between.
    """
    chunks = _split_into_chunks(text) if split_chunks else [text]
    last_idx = len(chunks) - 1

    for idx, chunk in enumerate(chunks):
        # Show typing indicator
        try:
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        except Exception:
            pass

        # Wait while "typing"
        delay = _typing_delay(chunk)
        await asyncio.sleep(delay)

        # Send the chunk — only attach keyboard to last chunk
        markup = reply_markup if idx == last_idx else None
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=chunk,
                parse_mode=parse_mode,
                reply_markup=markup,
            )
        except Exception as e:
            # Fallback without parse_mode if markdown fails
            await bot.send_message(
                chat_id=chat_id,
                text=chunk,
                reply_markup=markup,
            )

        # Pause between chunks
        if idx < last_idx:
            await asyncio.sleep(CHUNK_PAUSE)


async def send_quick(
    bot: Bot,
    chat_id: int,
    text: str,
    reply_markup=None,
    parse_mode: str = "Markdown",
):
    """
    Send a very short acknowledgement quickly (e.g. 'Got it!' or 'One sec...').
    """
    try:
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    except Exception:
        pass
    await asyncio.sleep(0.3)
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=parse_mode,
        reply_markup=reply_markup,
    )
