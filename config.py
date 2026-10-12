import os


BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

OWNER_ID = int(os.getenv("OWNER_ID", "0"))

CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "").strip()

CHANNEL_ID_RAW = os.getenv("CHANNEL_ID", "").strip()

if CHANNEL_ID_RAW:
    try:
        CHANNEL_ID = int(CHANNEL_ID_RAW)
    except ValueError:
        CHANNEL_ID = CHANNEL_ID_RAW
else:
    CHANNEL_ID = CHANNEL_USERNAME


JOIN_CHANNEL_TEXT = os.getenv(
    "JOIN_CHANNEL_TEXT",
    "📢 Join Channel",
)

VERIFY_BUTTON_TEXT = os.getenv(
    "VERIFY_BUTTON_TEXT",
    "✅ Verify",
)

GATE_MESSAGE = os.getenv(
    "GATE_MESSAGE",
    (
        "👋 Welcome {mention}!\n\n"
        "🔒 You need to join our channel before you can send messages in this group.\n\n"
        "1️⃣ Join the channel\n"
        "2️⃣ Come back here\n"
        "3️⃣ Press the ✅ Verify button\n\n"
        "After successful verification, your messaging permission will be restored."
    ),
)
