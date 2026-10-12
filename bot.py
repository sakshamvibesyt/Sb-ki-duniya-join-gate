import asyncio
import logging

from telegram import Update
from telegram.ext import (
Application,
ChatMemberHandler,
CommandHandler,
CallbackQueryHandler,
ContextTypes,
)

from config import BOT_TOKEN
from handlers.join_gate import handle_new_member, verify_callback
from handlers.admin import gate_command, ungate_command

logging.basicConfig(
format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
level=logging.INFO,
)

logger = logging.getLogger(name)

async def error_handler(
update: object,
context: ContextTypes.DEFAULT_TYPE,
):
logger.error(
"Exception while handling update:",
exc_info=context.error,
)

def main():
if not BOT_TOKEN:
raise ValueError(
"BOT_TOKEN is missing from Render Environment Variables."
)

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

app = Application.builder().token(BOT_TOKEN).build()

# Handle new members
app.add_handler(
    ChatMemberHandler(
        handle_new_member,
        ChatMemberHandler.CHAT_MEMBER,
    )
)

# Verification button
app.add_handler(
    CallbackQueryHandler(
        verify_callback,
        pattern=r"^verify$",
    )
)

# Admin commands
app.add_handler(CommandHandler("gate", gate_command))
app.add_handler(CommandHandler("ungate", ungate_command))

# Error handling
app.add_error_handler(error_handler)

logger.info("Join Gate Bot started.")

app.run_polling(
    allowed_updates=Update.ALL_TYPES,
    drop_pending_updates=True,
)

if name == "main":
main()
