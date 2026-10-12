from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from config import (
    OWNER_ID,
    GATE_MESSAGE,
    JOIN_CHANNEL_TEXT,
    VERIFY_BUTTON_TEXT,
)
from services.verification import (
    get_channel_link,
    is_admin,
)
from handlers.join_gate import unrestrict_user


async def gate_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.effective_chat or not update.effective_user:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Only admins can use /gate.
    if not await is_admin(chat_id, user_id, context):
        return

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    JOIN_CHANNEL_TEXT,
                    url=get_channel_link(),
                )
            ],
            [
                InlineKeyboardButton(
                    VERIFY_BUTTON_TEXT,
                    callback_data="verify",
                )
            ],
        ]
    )

    await update.effective_chat.send_message(
        text=GATE_MESSAGE.format(
            mention=update.effective_user.mention_html()
        ),
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def ungate_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.effective_chat or not update.effective_user:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Only admins can use /ungate.
    if not await is_admin(chat_id, user_id, context):
        return

    target_user_id = None

    # /ungate when replying to a user's message.
    if update.message and update.message.reply_to_message:
        target_user_id = update.message.reply_to_message.from_user.id

    # /ungate USER_ID
    elif context.args:
        try:
            target_user_id = int(context.args[0])
        except ValueError:
            target_user_id = None

    if not target_user_id:
        await update.effective_chat.send_message(
            "Usage:\n"
            "/ungate USER_ID\n\n"
            "Or reply to a user's message with /ungate."
        )
        return

    try:
        await unrestrict_user(
            chat_id,
            target_user_id,
            context,
        )

        await update.effective_chat.send_message(
            f"✅ User `{target_user_id}` has been un-gated.",
            parse_mode="Markdown",
        )

    except Exception:
        await update.effective_chat.send_message(
            "❌ Failed to un-gate this user."
      )
