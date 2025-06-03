# 🤖 Qwerty Bot

Qwerty is a feature-packed Discord bot built for **Kappa Theta Pi**. It helps with birthday reminders, reaction-based role assignments, fun commands, attendance tracking, and quick access to essential org info.

---

## 🚀 Features

### 🎉 Birthday Tools

- `!setbirthday MM-DD` — Set your birthday.
- `!removebirthday` — Delete your saved birthday.
- `!mybirthday` — Check your saved birthday.
- `!birthdayboard` — View a monthly birthday calendar with member names.
- ⏰ Sends **daily birthday wishes at 8 AM** with fun randomized messages.

### 🎭 Reaction Roles

- `!setuproles` _(admin only)_ — Posts a message where members can react to assign themselves roles.
- Adds or removes roles automatically when members react/unreact with specific emojis.

### 🗳️ Attendance Tracking

- Members can **DM a specific attendance code** (e.g. `ktp2025`) to log meeting attendance.
- After checking in, the bot sends a **fun follow-up question** to collect feedback.
- All responses are automatically **logged into a connected Google Sheet** with real names via a nickname/user ID mapping.
- `!export_realnames` _(owner only)_ — Generates `name_map.json` based on server display names for mapping.

### 📌 Org Info & Quick Links

- `!mastersheet` — Get the link to the master Google Sheet.
- `!eboard` — See current Eboard members.
- `!gboard` — See current Gboard members.

### 🎲 Fun Commands

- `!eightball <question>` — Ask the magic 8-ball a question.
- `!fact` — Get a random fun fact.
- `!vibecheck` — See if you pass the vibe check.
- `!coinflip` — Flip a coin.

---

## 🛠 Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/penut101/qwerty.git
cd qwerty-bot
```

### 2. Follow the ([Installation Guide](INSTALLATION_GUIDE.md))

- If you need any help feel free to reach out!!