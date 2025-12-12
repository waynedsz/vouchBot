import telebot
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # e.g. "-1001234567890"

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
        admin_ids = [admin.user.id for admin in admins]
        return user_id in admin_ids
    except:
        return False


# ------------------------------
# Pinned message creation
# ------------------------------

def formatted_message(count):
    return (
        "🔥 <b>Vouch Counter</b> 🔥\n\n"
        f"<b>Total Vouches:</b> {count}\n\n"
        "(Forward messages containing the word 'vouch')"
    )


def get_or_create_pinned_message():
    pinned = bot.get_chat(CHANNEL_ID).pinned_message
    if pinned:
        return pinned.message_id

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

    # ensure we are in the channel
    if str(message.chat.id) != CHANNEL_ID:
        return

    # admin check
    if not is_admin(message.from_user.id):
        return

    count = load_counter()
    if count > 0:
        count -= 1
        save_counter(count)

        bot.edit_message_text(
            formatted_message(count),
            chat_id=CHANNEL_ID,
            message_id=pinned_message_id,
            parse_mode="HTML"
        )

    # (optional) delete your /dec command message
    bot.delete_message(message.chat.id, message.message_id)


# Optional: /reset command
@bot.message_handler(commands=['reset'])
def reset(message):
    global pinned_message_id

    if str(message.chat.id) != CHANNEL_ID:
        return

    if not is_admin(message.from_user.id):
        return

    save_counter(0)

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

    # Only count forwarded messages
    if not message.forward_from and not message.forward_from_chat:
        return

    # account for text or caption
    text = message.text or message.caption or ""

    if "vouch" in text.lower():
        count = load_counter() + 1
        save_counter(count)

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
