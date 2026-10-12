from telegram.ext import ContextTypes
from telegram.error import TelegramError

from config import CHANNEL_ID, CHANNEL_USERNAME


async def is_admin(
    chat_id: int,
    user_id: int,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    try:
        member = await context.bot.get_chat_member(
            chat_id=chat_id,
            user_id=user_id,
        )

        return member.status in (
            "administrator",
            "creator",
        )

    except TelegramError:
        return False


async def is_channel_member(
    user_id: int,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_ID,
            user_id=user_id,
        )

        return member.status in (
            "member",
            "administrator",
            "creator",
        )

    except TelegramError:
        return False


def get_channel_link() -> str:
    if CHANNEL_USERNAME:
        username = CHANNEL_USERNAME

        if username.startswith("https://t.me/"):
            return username

        if username.startswith("@"):
            username = username[1:]

        return f"https://t.me/{username}"

    return "https://t.me/"
