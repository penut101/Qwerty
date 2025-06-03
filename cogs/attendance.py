# This is a cog for the Qwerty Bot
# It contains attendance management commands that users can interact with.
# Written by Aiden Nemeroff

# Dependencies Needed:
# python-dotenv
# discord.py
# gspread
# oauth2client
import discord
from discord.ext import commands
import os
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables from .env file (Grab the Google Sheets ID and attendance code)
load_dotenv()

# Environment variables for Google Sheets and attendance code
SHEET_ID = os.getenv("SHEET_ID")
ATTENDANCE_CODE = os.getenv("ATTENDANCE_CODE")

# Load name map from file
with open("name_map.json", "r", encoding="utf-8") as f:
    ID_MAP = json.load(f)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# Authenticate using the service account credentials (this is the JSON file you downloaded from Google Cloud Console)
creds = ServiceAccountCredentials.from_json_keyfile_name("qwerty-attendance-4f218a2cad1f.json", scope)
# Authorize the client (this is the client that will interact with Google Sheets gotten from the creds)
client = gspread.authorize(creds)
# Open the Google Sheet by its ID and select the first sheet
# This can be changed to select a different sheet if needed (like a second semester sheet)
sheet = client.open_by_key(SHEET_ID).sheet1

# Random follow-up questions
questions = [
    "How do you like this feature?",
    "What would you like to see improved?",
    "Do you have any suggestions for new features?",
    "What is your favorite part of the bot?",
]

# This cog handles attendance tracking and response logging
class Attendance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # This dictionary will hold users who are awaiting a response after entering the attendance code
        self.awaiting_response = {}
    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots and non-DM channels
        if message.author.bot or not isinstance(message.channel, discord.DMChannel):
            return
        # Ignore messages that don't match the attendance code
        user = message.author
        content = message.content.strip().lower()

        # Step 1: Code entry
        if content == ATTENDANCE_CODE:
            # Mark down the user's attendance with a timestamp and a random question
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            question = random.choice(questions)

            # Get the username and real name from the ID_MAP
            # If the user is not in the ID_MAP, use their username as a fallback
            username = str(user)
            real_name = ID_MAP.get(str(user.id), "Unknown")

            # Organized the data to be stored in the dictionary and ready for the Google Sheet
            self.awaiting_response[user.id] = {
                "username": username,
                "real_name": real_name,
                "timestamp": timestamp,
                "question": question
            }
            # Mark the user as having entered the attendance code and reply with a confirmation message
            await user.send(
                f"✅ Thanks {real_name if real_name != 'Unknown' else username}! Your attendance has been recorded.\n\n"
                f"🧠 Quick question:\n**{question}**"
            )

        # Step 2: Response logging
        # If the user is awaiting a response, log their answer and remove them from the awaiting list
        elif user.id in self.awaiting_response:
            data = self.awaiting_response.pop(user.id)
            answer = message.content.strip()
            # Create a new row with the user's data and their answer
            row = [data["username"], data["real_name"], data["timestamp"], data["question"], answer]
            # Append the row to the Google Sheet
            sheet.append_row(row)
            # Notify the user that their response has been recorded
            await user.send("📌 Thanks! Your response has been recorded.")
        else:
            await user.send("❌ Invalid code. Please try again with the correct attendance phrase.")

async def setup(bot):
    await bot.add_cog(Attendance(bot))
