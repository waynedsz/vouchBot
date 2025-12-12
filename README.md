# Telegram Vouch Counter Bot

A lightweight, free Telegram bot that counts **vouches** in a Telegram channel and displays the total in a **pinned message**.  
Built to be simple, forkable, and safe for public GitHub repositories.

---

## ✨ Features

- Automatically creates and pins a **Vouch Counter**
- Increments when a **forwarded message** contains the keyword `vouch`
- Works with **text messages and photo captions**
- **Admin-only** management commands
- Optional **image** in the pinned message (via Telegram `file_id`)
- **Persistent counter** (restores state by reading the pinned message)
- No database required
- No hardcoded personal data

---

## 📌 How It Works

1. Add the bot as an **admin** to your channel  
2. On first run, the bot creates and pins a counter message  
3. You forward messages into the channel  
4. If a forwarded message contains `vouch`, the counter increases  
5. If the bot restarts, it restores the count from the pinned message  

---

## 🔧 Requirements

- Python 3.9+
- Telegram bot token (from **@BotFather**)
- A Telegram channel where the bot is an admin
- `pyTelegramBotAPI`

---

## 📁 Project Structure

.
├── main.py
├── requirements.txt
├── counter.txt        # ignored by git
├── .gitignore
└── .github/
    └── workflows/
        └── workflow.yml

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables / Secrets

This project is designed to use **GitHub Secrets** (or environment variables).

### Required

- `BOT_TOKEN` – Your Telegram bot token  
- `CHANNEL_ID` – Your Telegram channel ID (starts with `-100`)  
- `DISPLAY_NAME` – Name shown in the pinned message  
- `IMAGE_FILE_ID` – Telegram `file_id` of an image for the pinned message  
- `VOUCH_USERNAME` - Set it to your Telegram user (inc. @) to allow hidden forwards to count.

---

## 🖼️ Adding an Image (Optional)

The bot uses **Telegram `file_id`**, not public image hosting.

### Steps

1. Download your image  
2. Send it to your bot in a private chat  
3. Forward that image to **@RawDataBot**  
4. Copy the **largest `file_id`** from the response  
5. Save it as a GitHub secret named `IMAGE_FILE_ID`  

If `IMAGE_FILE_ID` is not set, the bot will create a **text-only** pinned message.

---

## 👮 Admin Commands

All commands are **admin-only** and automatically deleted to keep the channel clean.

- `/dec` – Decrease the counter by 1  
- `/setcount <number>` – Set the counter to an exact value  
- `/reset` – Reset the counter to 0  

---

## 📌 Pinned Message Example

🔵 Vouch Counter  

username's Total Vouches: 12

---

## 🔁 Persistence

The bot does **not** rely on a database.

On startup, it:
- Reads the pinned message
- Extracts the current vouch count
- Restores the counter automatically

This makes it suitable for **free hosting** and restarts without data loss.

---

## 🚀 Running the Bot

### Locally

```bash
python main.py
```

### GitHub Actions

- Add the required secrets
- Run the workflow manually (`workflow_dispatch`)
- No commits are needed to start or restart the bot

---

## ⚠️ Notes & Limitations

- Telegram does not notify bots when messages are deleted  
  → use `/dec` when removing a vouch manually
- Only **forwarded messages** are counted
- Keyword detection is **case-insensitive**
- This bot is designed for **Telegram channels**

---

## 📜 License

MIT License

---

## 🤝 Contributing

Pull requests, improvements, and suggestions are welcome.
