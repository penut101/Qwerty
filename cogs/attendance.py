# This is a cog for the Qwerty Bot
# It contains attendance management commands that users can interact with.
# Written by Aiden Nemeroff

import discord
from discord.ext import commands
import os
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv
import json

load_dotenv()

# Environment variables
SHEET_ID = os.getenv("SHEET_ID")
ATTENDANCE_CODE = os.getenv("ATTENDANCE_CODE")

# Load name map from file
with open("name_map.json", "r", encoding="utf-8") as f:
    ID_MAP = json.load(f)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# Authenticate using the service account credentials
creds = ServiceAccountCredentials.from_json_keyfile_name("qwerty-attendance-4f218a2cad1f.json", scope)
# Authorize the client
client = gspread.authorize(creds)
# Open the Google Sheet by its ID and select the first sheet
sheet = client.open_by_key(SHEET_ID).sheet1

# Random follow-up questions
questions = [
    "What was your biggest takeaway from the meeting?",
    "What do you want to see next time?",
    "How was your experience today?",
    "What did you learn today?",
    "Rate today’s meeting from 1–10!"
]
# This cog handles attendance tracking and response logging for a Discord bot.
class Attendance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.awaiting_response = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not isinstance(message.channel, discord.DMChannel):
            return

        user = message.author
        content = message.content.strip().lower()

        # Step 1: Code entry
        if content == ATTENDANCE_CODE:
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            question = random.choice(questions)

            username = str(user)
            real_name = ID_MAP.get(str(user.id), "Unknown")

            self.awaiting_response[user.id] = {
                "username": username,
                "real_name": real_name,
                "timestamp": timestamp,
                "question": question
            }

            await user.send(
                f"✅ Thanks {real_name if real_name != 'Unknown' else username}! Your attendance has been recorded.\n\n"
                f"🧠 Quick question:\n**{question}**"
            )

        # Step 2: Response logging
        elif user.id in self.awaiting_response:
            data = self.awaiting_response.pop(user.id)
            answer = message.content.strip()

            row = [data["username"], data["real_name"], data["timestamp"], data["question"], answer]
            sheet.append_row(row)

            await user.send("📌 Thanks! Your response has been recorded.")
        else:
            await user.send("❌ Invalid code. Please try again with the correct attendance phrase.")

async def setup(bot):
    await bot.add_cog(Attendance(bot))
