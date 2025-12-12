# Telegram Vouch Counter Bot

A simple, free Telegram bot that automatically counts **vouches** in a Telegram channel and displays the total in a **pinned message**.

Designed to be:
- beginner-friendly
- fully free
- safe for public GitHub repos
- easy to fork and customise

---

## ✨ Features

- Automatically creates and pins a **Vouch Counter** message
- Increments the counter when a **forwarded message** contains the word `vouch`
- Supports **text messages and photo captions**
- Admin-only commands to manage the counter
- Optional **image** in the pinned message (using Telegram `file_id`)
- **Persistent counter** (survives restarts by reading the pinned message)
- No database required
- No hardcoded personal data

---

## 📌 How it works

1. The bot is added as an **admin** to a channel  
2. If no pinned message exists, it creates one  
3. You forward messages into the channel  
4. If a forwarded message contains `vouch`, the counter increases  
5. On restart, the bot restores the counter from the pinned message  

---

## 🔧 Requirements

- Python 3.9+
- Telegram bot token (via **@BotFather**)
- Telegram channel where the bot is an admin
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

### 1. Clone the repo

git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git  
cd YOUR_REPO

### 2. Install dependencies

pip install -r requirements.txt

---

## 🔐 Environment Variables / Secrets

This project uses **GitHub Secrets** (or environment variables).

### Required

- BOT_TOKEN – Telegram bot token  
- CHANNEL_ID – Telegram channel ID (starts with `-100`)  

### Optional (recommended)

- DISPLAY_NAME – Name shown in the pinned message  
- IMAGE_FILE_ID – Telegram `file_id` for an image  

---

## 🖼️ How to add an image (optional)

This bot uses **Telegram `file_id`**, not public image hosting.

Steps:
1. Download your image  
2. Send it to any Telegram chat  
3. Forward the image to **@RawDataBot**  
4. Copy the **largest `file_id`**  
5. Save it as a secret named `IMAGE_FILE_ID`  

If no image is set, the bot uses a text-only pinned message.

---

## 👮 Admin Commands

All commands are **admin-only** and auto-delete.

- /dec – Decrease the counter by 1  
- /setcount <number> – Set the counter to an exact value  
- /reset – Reset the counter to 0  

---

## 📌 Pinned Message Format

🔵 Vouch Counter  

<DISPLAY_NAME>'s Total Vouches: 12

---

## 🔁 Persistence

The bot restores the counter by reading the **pinned message** on startup.

- No database
- Free hosting friendly
- Restarts do not reset the count

---

## 🚀 Running the bot

### Locally

python main.py

### GitHub Actions

- Add the secrets
- Run the workflow manually (`workflow_dispatch`)
- No commits required

---

## ⚠️ Notes & Limitations

- Telegram does not notify bots when messages are deleted  
  → use `/dec` when removing a vouch manually
- Only forwarded messages are counted
- Keyword detection is case-insensitive

---

## 📜 License

MIT License

---

## 🤝 Contributing

Pull requests and improvements are welcome.
