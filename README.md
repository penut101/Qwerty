# 🧰 Qwerty Bot Installation & Setup Guide

Welcome to the setup guide for **Qwerty**, the all-in-one Discord bot built for Kappa Theta Pi. This guide will walk you through everything you need to clone, configure, and run the bot on your own server.

---

## ✅ Prerequisites

- Python 3.10 or later
- pip (Python package installer)
- Git (optional)
- A Discord bot token ([create one here](https://discord.com/developers/applications))
- (Optional) Google Sheets service credentials for attendance logging

---

## 📥 Step 1: Clone the Repository

Clone the bot using Git:

```bash
git clone https://github.com/penut101/qwerty.git
cd qwerty-bot
```

Or download the ZIP from GitHub and extract it manually.

---

## 📦 Step 2: Install Dependencies

Ensure you're in the project folder and run:

```bash
pip install -r requirements.txt
```

---

## 🔐 Step 3: Set Up Environment Variables

Create a `.env` file in the root directory of the project and add:

```
DISCORD_TOKEN=your_discord_bot_token
BIRTHDAY_CHANNEL_ID=your_channel_id_here
```

If using Google Sheets for attendance, also include:

```
GOOGLE_SHEETS_CREDENTIALS=path/to/your/credentials.json
```

> ⚠️ Make sure `.env` and your credentials JSON file are **not** committed to your repo.

---

## 🚀 Step 4: Run the Bot

Run the bot with:

```bash
python bot.py
```

You should see:
```
✅ Bot is ready! Logged in as Qwerty#XXXX
```

---

## 🧪 Step 5: Invite Qwerty to Your Server

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Under your bot application, go to **OAuth2 > URL Generator**.
3. Select:
   - **Scopes**: `bot`
   - **Bot Permissions**: `Send Messages`, `Manage Roles`, `Read Message History`, etc.
4. Copy the generated invite link and open it in your browser.
5. Select the server and invite Qwerty.

---

## 🗂 Folder Structure

```
qwerty-bot/
├── bot.py                # Main bot launcher
├── .env                  # Secret environment variables (not included in repo)
├── requirements.txt      # Dependency list
├── cogs/                 # Modular bot commands
│   ├── birthdays.py
│   ├── roles.py
│   ├── attendance.py
│   ├── helper.py
│   ├── fun.py
│   ├── rainbow.py
│   ├── typefight.py
│   ├── hangman.py
│   ├── wordscramble.py
│   └── export_members.py
└── README.md             # Feature overview and usage
```

---

## 🔧 Optional Configuration

You can customize:
- Roles and emojis in `roles.py`
- Birthday message styles and timezone in `birthdays.py`
- Google Sheet logic in `attendance.py`
- Add new commands to `fun.py` or make your own cog

---

## 💬 Need Help?

Feel free to reach out at **aidennemeroff@gmail.com**
