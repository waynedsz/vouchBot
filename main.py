import telebot
import os
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # e.g. "-1001234567890"
DISPLAY_NAME = os.getenv("DISPLAY_NAME", "User")

# Telegram image file_id (set as GitHub Secret)
IMAGE_FILE_ID = os.getenv("IMAGE_FILE_ID")

bot = telebot.TeleBot(BOT_TOKEN)

COUNTER_FILE = "counter.txt"
pinned_message_id = None


# ------------------------------
# Counter helpers
# ------------------------------

def load_counter():
    if not os.path.exists(COUNTER_FILE):
        return 0
    with open(COUNTER_FILE, "r") as f:
        return int(f.read().strip())


def save_counter(value):
    with open(COUNTER_FILE, "w") as f:
        f.write(str(value))


# ------------------------------
# Admin check helper
# ------------------------------

def is_admin(user_id):
    try:
        admins = bot.get_chat_administrators(CHANNEL_ID)
        return user_id in [admin.user.id for admin in admins]
    except:
        return False


# ------------------------------
# Pinned message helpers
# ------------------------------

def formatted_message(count):
    return (
        "🔵 <b>Vouch Counter</b>\n\n"
        f"<b>{DISPLAY_NAME}'s Total Vouches:</b> {count}\n\n"
    )


def extract_count_from_pinned(pinned):
    """
    Reads the pinned message text/caption and extracts the number.
    Returns None if not found.
    """
    text = pinned.caption or pinned.text or ""
    match = re.search(r"Total Vouches:</b>\s*(\d+)", text)
    if match:
        return int(match.group(1))
    return None


def ensure_pinned_message():
    """
    Ensures a pinned message exists AND syncs the counter from Telegram.
    """
    global pinned_message_id

    chat = bot.get_chat(CHANNEL_ID)
    pinned = chat.pinned_message

    # If pinned message exists, sync counter from it
    if pinned:
        pinned_message_id = pinned.message_id

        extracted = extract_count_from_pinned(pinned)
        if extracted is not None:
            save_counter(extracted)

        return

    # No pinned message → create one
    count = load_counter()

    if IMAGE_FILE_ID:
        msg = bot.send_photo(
            CHANNEL_ID,
            IMAGE_FILE_ID,
            caption=formatted_message(count),
            parse_mode="HTML"
        )
    else:
        msg = bot.send_message(
            CHANNEL_ID,
            formatted_message(count),
            parse_mode="HTML"
        )

    bot.pin_chat_message(CHANNEL_ID, msg.message_id)
    pinned_message_id = msg.message_id


def update_pinned_message(count):
    pinned = bot.get_chat(CHANNEL_ID).pinned_message

    if pinned and pinned.photo:
        bot.edit_message_caption(
            caption=formatted_message(count),
            chat_id=CHANNEL_ID,
            message_id=pinned_message_id,
            parse_mode="HTML"
        )
    else:
        bot.edit_message_text(
            formatted_message(count),
            chat_id=CHANNEL_ID,
            message_id=pinned_message_id,
            parse_mode="HTML"
        )


# ------------------------------
# Admin Commands
# ------------------------------

@bot.message_handler(commands=['dec'])
def dec(message):
    if str(message.chat.id) != CHANNEL_ID:
        return
    if not is_admin(message.from_user.id):
        return

    ensure_pinned_message()

    count = load_counter()
    if count > 0:
        count -= 1
        save_counter(count)
        update_pinned_message(count)

    bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(commands=['setcount'])
def setcount(message):
    if str(message.chat.id) != CHANNEL_ID:
        return
    if not is_admin(message.from_user.id):
        return

    ensure_pinned_message()

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.delete_message(message.chat.id, message.message_id)
        return

    new_count = int(parts[1])
    save_counter(new_count)
    update_pinned_message(new_count)

    bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(commands=['reset'])
def reset(message):
    if str(message.chat.id) != CHANNEL_ID:
        return
    if not is_admin(message.from_user.id):
        return

    ensure_pinned_message()

    save_counter(0)
    update_pinned_message(0)

    bot.delete_message(message.chat.id, message.message_id)


# ------------------------------
# Message Handler (vouch detector)
# ------------------------------

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if str(message.chat.id) != CHANNEL_ID:
        return

    ensure_pinned_message()

    if not message.forward_from and not message.forward_from_chat:
        return

    text = message.text or message.caption or ""
    if "vouch" in text.lower():
        count = load_counter() + 1
        save_counter(count)
        update_pinned_message(count)


# ------------------------------
# Start bot
# ------------------------------

if __name__ == "__main__":
    ensure_pinned_message()
    bot.polling(none_stop=True)
