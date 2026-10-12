import logging
import asyncio

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions,
)
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from config import (
    GATE_MESSAGE,
    JOIN_CHANNEL_TEXT,
    VERIFY_BUTTON_TEXT,
)
from services.verification import (
    is_admin,
    is_channel_member,
    get_channel_link,
)

logger = logging.getLogger(__name__)


async def restrict_user(
    chat_id: int,
    user_id: int,
    context: ContextTypes.DEFAULT_TYPE,
):
    permissions = ChatPermissions(
        can_send_messages=False,
        can_send_audios=False,
        can_send_documents=False,
        can_send_photos=False,
        can_send_videos=False,
        can_send_video_notes=False,
        can_send_voice_notes=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_change_info=False,
        can_invite_users=False,
        can_pin_messages=False,
        can_manage_topics=False,
    )

    await context.bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=permissions,
    )


async def unrestrict_user(
    chat_id: int,
    user_id: int,
    context: ContextTypes.DEFAULT_TYPE,
):
    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_audios=True,
        can_send_documents=True,
        can_send_photos=True,
        can_send_videos=True,
        can_send_video_notes=True,
        can_send_voice_notes=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_invite_users=True,
        can_pin_messages=False,
        can_manage_topics=True,
    )

    await context.bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=permissions,
    )


async def handle_new_member(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.chat_member:
        return

    chat_member_update = update.chat_member

    old_status = chat_member_update.old_chat_member.status
    new_status = chat_member_update.new_chat_member.status

    if new_status not in ("member", "restricted"):
        return

    if old_status in (
        "member",
        "administrator",
        "creator",
        "restricted",
    ):
        return

    chat = chat_member_update.chat
    user = chat_member_update.new_chat_member.user

    if user.is_bot:
        return

    try:
        # Admins ko gate nahi karna.
        if await is_admin(chat.id, user.id, context):
            return

        # User ko immediately restrict karo.
        await restrict_user(
            chat.id,
            user.id,
            context,
        )

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

        text = GATE_MESSAGE.format(
            mention=user.mention_html(),
        )

        message = await context.bot.send_message(
            chat_id=chat.id,
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )

        context.application.bot_data.setdefault(
            "gate_messages",
            {},
        )

        context.application.bot_data["gate_messages"][
            (chat.id, user.id)
        ] = message.message_id

    except TelegramError:
        logger.exception(
            "Failed to process new member."
        )


async def verify_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if not query:
        return

    user = query.from_user

    if not query.message:
        return

    chat = query.message.chat

    try:
        if await is_admin(
            chat.id,
            user.id,
            context,
        ):
            await query.answer(
                "You are already an admin.",
                show_alert=True,
            )
            return

        # Channel membership check.
        joined = await is_channel_member(
            user.id,
            context,
        )

        if not joined:
            await query.answer(
                "❌ Please join the channel first.",
                show_alert=True,
            )
            return

        # Verification successful.
        await unrestrict_user(
            chat.id,
            user.id,
            context,
        )

        await query.answer(
            "✅ Verification successful!",
            show_alert=True,
        )

        # Gate message delete.
        try:
            await query.message.delete()
        except TelegramError:
            pass

        success_message = await context.bot.send_message(
            chat_id=chat.id,
            text=(
                f"✅ {user.mention_html()} "
                "verified successfully!\n\n"
                "You can now send messages in the group."
            ),
            parse_mode="HTML",
        )

        # Success message automatically delete.
        asyncio.create_task(
            delete_later(
                context,
                chat.id,
                success_message.message_id,
                8,
            )
        )

        context.application.bot_data.get(
            "gate_messages",
            {},
        ).pop(
            (chat.id, user.id),
            None,
        )

    except TelegramError:
        logger.exception(
            "Verification error."
        )

        try:
            await query.answer(
                "⚠️ Verification failed. Try again.",
                show_alert=True,
            )
        except TelegramError:
            pass


async def delete_later(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    message_id: int,
    delay: int,
):
    await asyncio.sleep(delay)

    try:
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )
    except TelegramError:
        pass
