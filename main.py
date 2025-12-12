import telebot
import os
import re
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # e.g. "-1001234567890"
DISPLAY_NAME = os.getenv("DISPLAY_NAME", "User")

# Telegram image file_id (set as GitHub Secret)
IMAGE_FILE_ID = os.getenv("IMAGE_FILE_ID")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

COUNTER_FILE = "counter.txt"
pinned_message_id = None
last_edit_time = 0.0   # ⬅️ throttle timestamp


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
        f"🔷 {DISPLAY_NAME}'s Total Vouches: {count}\n\n"
        "Here you can find all of my vouches.\n\n"
        "👉 @wdszn"
    )


def extract_count_from_pinned(pinned):
    text = pinned.caption or pinned.text or ""
    match = re.search(r"Total Vouches:.*?(\d+)", text)
    return int(match.group(1)) if match else None


def ensure_pinned_message():
    global pinned_message_id

    chat = bot.get_chat(CHANNEL_ID)
    pinned = chat.pinned_message

    if pinned:
        pinned_message_id = pinned.message_id
        extracted = extract_count_from_pinned(pinned)
        if extracted is not None:
            save_counter(extracted)
        return

    count = load_counter()

    if IMAGE_FILE_ID:
        msg = bot.send_photo(
            CHANNEL_ID,
            IMAGE_FILE_ID,
            caption=formatted_message(count)
        )
    else:
        msg = bot.send_message(
            CHANNEL_ID,
            formatted_message(count)
        )

    bot.pin_chat_message(CHANNEL_ID, msg.message_id)
    pinned_message_id = msg.message_id


def throttled_update_pinned_message(count):
    """Edit pinned message at most once every ~1.2 seconds"""
    global last_edit_time

    now = time.time()
    if now - last_edit_time < 1.2:
        return

    last_edit_time = now
    pinned = bot.get_chat(CHANNEL_ID).pinned_message

    try:
        if pinned and pinned.photo:
            bot.edit_message_caption(
                caption=formatted_message(count),
                chat_id=CHANNEL_ID,
                message_id=pinned_message_id
            )
        else:
            bot.edit_message_text(
                formatted_message(count),
                chat_id=CHANNEL_ID,
                message_id=pinned_message_id
            )
    except:
        pass


# ------------------------------
# Admin Commands (CHANNEL)
# ------------------------------

@bot.channel_post_handler(commands=['dec'])
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
        throttled_update_pinned_message(count)

    bot.delete_message(message.chat.id, message.message_id)


@bot.channel_post_handler(commands=['setcount'])
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
    throttled_update_pinned_message(new_count)

    bot.delete_message(message.chat.id, message.message_id)


@bot.channel_post_handler(commands=['reset'])
def reset(message):
    if str(message.chat.id) != CHANNEL_ID:
        return
    if not is_admin(message.from_user.id):
        return

    ensure_pinned_message()

    save_counter(0)
    throttled_update_pinned_message(0)

    bot.delete_message(message.chat.id, message.message_id)


# ------------------------------
# Channel post handler (vouch detector)
# ------------------------------

@bot.channel_post_handler(func=lambda message: True)
def handle_channel_posts(message):
    if str(message.chat.id) != CHANNEL_ID:
        return

    ensure_pinned_message()

    if not message.forward_from and not message.forward_from_chat:
        return

    text = message.text or message.caption or ""
    if "vouch" in text.lower():
        count = load_counter() + 1
        save_counter(count)
        throttled_update_pinned_message(count)


# ------------------------------
# Start bot
# ------------------------------

if __name__ == "__main__":
    ensure_pinned_message()
    bot.polling(none_stop=True)
