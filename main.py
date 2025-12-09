import telebot
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # example: "-1001234567890"

bot = telebot.TeleBot(BOT_TOKEN)

COUNTER_FILE = "counter.txt"


def load_counter():
    if not os.path.exists(COUNTER_FILE):
        return 0
    with open(COUNTER_FILE, "r") as f:
        return int(f.read().strip())


def save_counter(value):
    with open(COUNTER_FILE, "w") as f:
        f.write(str(value))


def get_or_create_pinned_message():
    pinned = bot.get_chat(CHANNEL_ID).pinned_message
    if pinned:
        return pinned.message_id

    msg = bot.send_message(CHANNEL_ID, f"Vouches: {load_counter()}")
    bot.pin_chat_message(CHANNEL_ID, msg.message_id)
    return msg.message_id


pinned_message_id = None


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    global pinned_message_id

    # Ensure we are only listening inside the channel
    if str(message.chat.id) != CHANNEL_ID:
        return

    # Ensure pinned message exists
    if pinned_message_id is None:
        pinned_message_id = get_or_create_pinned_message()

    # Only count forwarded messages
    if not message.forward_from and not message.forward_from_chat:
        return

    # Detect "vouch" keyword in forwarded text
    if message.text and "vouch" in message.text.lower():
        
        count = load_counter() + 1
        save_counter(count)

        # Update pinned vouch count
        bot.edit_message_text(
            f"Vouches: {count}",
            chat_id=CHANNEL_ID,
            message_id=pinned_message_id
        )



if __name__ == "__main__":
    pinned_message_id = get_or_create_pinned_message()
    bot.polling(none_stop=True)
