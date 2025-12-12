import telebot
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # e.g. "-1001234567890"
DISPLAY_NAME = os.getenv("DISPLAY_NAME", "User")

# Telegram image file_id (set as GitHub Secret)
IMAGE_FILE_ID = os.getenv("IMAGE_FILE_ID")

bot = telebot.TeleBot(BOT_TOKEN)

COUNTER_FILE = "counter.txt"


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
# Pinned message formatting
# ------------------------------

def formatted_message(count):
    return (
        "🔵 <b>Vouch Counter</b>\n\n"
        f"<b>{DISPLAY_NAME}'s Total Vouches:</b> {count}\n\n"
    )


def get_or_create_pinned_message():
    pinned = bot.get_chat(CHANNEL_ID).pinned_message
    if pinned:
        return pinned.message_id

    # If IMAGE_FILE_ID is set, send photo with caption
    if IMAGE_FILE_ID:
        msg = bot.send_photo(
            CHANNEL_ID,
            IMAGE_FILE_ID,
            caption=formatted_message(load_counter()),
            parse_mode="HTML"
        )
    else:
        # Fallback: text-only pinned message
        msg = bot.send_message(
            CHANNEL_ID,
            formatted_message(load_counter()),
            parse_mode="HTML"
        )

    bot.pin_chat_message(CHANNEL_ID, msg.message_id)
    return msg.message_id


pinned_message_id = None


# ------------------------------
# Admin Commands
# ------------------------------

@bot.message_handler(commands=['dec'])
def dec(message):
    global pinned_message_id

    if str(message.chat.id) != CHANNEL_ID:
        return

    if not is_admin(message.from_user.id):
        return

    if pinned_message_id is None:
        pinned_message_id = get_or_create_pinned_message()

    count = load_counter()
    if count > 0:
        count -= 1
        save_counter(count)

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

    bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(commands=['setcount'])
def setcount(message):
    global pinned_message_id

    if str(message.chat.id) != CHANNEL_ID:
        return

    if not is_admin(message.from_user.id):
        return

    if pinned_message_id is None:
        pinned_message_id = get_or_create_pinned_message()

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.delete_message(message.chat.id, message.message_id)
        return

    new_count = int(parts[1])
    save_counter(new_count)

    pinned = bot.get_chat(CHANNEL_ID).pinned_message
    if pinned and pinned.photo:
        bot.edit_message_caption(
            caption=formatted_message(new_count),
            chat_id=CHANNEL_ID,
            message_id=pinned_message_id,
            parse_mode="HTML"
        )
    else:
        bot.edit_message_text(
            formatted_message(new_count),
            chat_id=CHANNEL_ID,
            message_id=pinned_message_id,
            parse_mode="HTML"
        )

    bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(commands=['reset'])
def reset(message):
    global pinned_message_id

    if str(message.chat.id) != CHANNEL_ID:
        return

    if not is_admin(message.from_user.id):
        return

    if pinned_message_id is None:
        pinned_message_id = get_or_create_pinned_message()

    save_counter(0)

    pinned = bot.get_chat(CHANNEL_ID).pinned_message
    if pinned and pinned.photo:
        bot.edit_message_caption(
            caption=formatted_message(0),
            chat_id=CHANNEL_ID,
            message_id=pinned_message_id,
            parse_mode="HTML"
        )
    else:
        bot.edit_message_text(
            formatted_message(0),
            chat_id=CHANNEL_ID,
            message_id=pinned_message_id,
            parse_mode="HTML"
        )

    bot.delete_message(message.chat.id, message.message_id)


# ------------------------------
# Message Handler (vouch detector)
# ------------------------------

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    global pinned_message_id

    if str(message.chat.id) != CHANNEL_ID:
        return

    if pinned_message_id is None:
        pinned_message_id = get_or_create_pinned_message()

    if not message.forward_from and not message.forward_from_chat:
        return

    text = message.text or message.caption or ""
    if "vouch" in text.lower():
        count = load_counter() + 1
        save_counter(count)

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
# Start bot
# ------------------------------

if __name__ == "__main__":
    pinned_message_id = get_or_create_pinned_message()
    bot.polling(none_stop=True)
