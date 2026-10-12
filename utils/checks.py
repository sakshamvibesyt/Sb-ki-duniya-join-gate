from telegram.error import TelegramError


async def user_is_admin(
    bot,
    chat_id: int,
    user_id: int,
) -> bool:
    try:
        member = await bot.get_chat_member(
            chat_id=chat_id,
            user_id=user_id,
        )

        return member.status in (
            "administrator",
            "creator",
        )

    except TelegramError:
        return False
