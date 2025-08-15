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
import json
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
SHEET_ID = os.getenv("SHEET_ID")

# Load name map (Discord ID → Real Name)
with open("name_map.json", "r", encoding="utf-8") as f:
    ID_MAP = json.load(f)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# Authenticate using the service account credentials (this is the JSON file you downloaded from Google Cloud Console)
creds = ServiceAccountCredentials.from_json_keyfile_name("qwerty-attendance-4f218a2cad1f.json", scope)
# Authorize the client (this is the client that will interact with Google Sheets gotten from the creds)
client = gspread.authorize(creds)
# Open the Google Sheet by its ID and select the first sheet (you can change this to select a different sheet 
# Example: Differnet sheets for different semesters
sheet = client.open_by_key(SHEET_ID).sheet1

# Attendance config file
CONFIG_FILE = "attendance_config.json"

# load or initialize the attendance codes configuration
def load_codes():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("codes", {})
    
# Save a new attendance code for an event
def save_code(event_name, code):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["codes"][event_name.lower()] = code.strip().lower()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
# Get the event name by its code
def get_event_by_code(code):
    codes = load_codes()
    for event, event_code in codes.items():
        if event_code == code.strip().lower():
            return event
    return None

# Random questions to ask users after they check in
questions = [
    "How do you like this feature?",
    "What would you like to see improved?",
    "Do you have any suggestions for new features?",
    "What is your favorite part of the bot?",
]

# Event-specific questions
event_questions = {
    "volunteer hours": [
        "How many hours did you volunteer for?"
    ],
    "brotherhood event": [
        "1. Post Picture to Photo Circle: 1 point\n2. Attend a Rush Event as a Brother: 1 point \n3. Hanging out with KTP Brothers outside of Chapter: 1 point\n4. Going to KTP Social Event\n5. Attend Study Hours: 1 point\n6. Post KTP Related Content on Social Media (Reposting does not count): 1 point\n7. Wear KTP T-Shirt: 1 point\n8. Partake in Hackathon: 3 points"
    ],
    "networking event": [
        "1. Attend a fundraising Event: 1 point\n2. Attend a Philanthropy Event: 1 point\n3. Attend a Networking Event: 1 point\n4. Attending Career Fair: 1 point\n5. Help with recruitment/referring new brothers: 2 points",
    ],
    "chapter meeting": [
        "Did you find the meeting productive?",
        "What topics were most relevant to you?",
        "Any suggestions for the next meeting?"
    ],
    "board meeting": [
        "What insights did you gain from today’s meeting?",
        "What would you change for the next one?",
        "Were your concerns addressed?",
        "Anything to add for next time?"
    ]
}

class Attendance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.awaiting_response = {}

    # Helper method to check if the user has the Admin role in any of the bot's guilds
    async def is_admin(self, ctx):
        for guild in self.bot.guilds:
            member = guild.get_member(ctx.author.id)
            if member and any(role.name == "Admin" for role in member.roles):
                return True
        return False

    # Listen for DMs to check attendance codes and log responses
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not isinstance(message.channel, discord.DMChannel):
            return

        user = message.author
        content = message.content.strip().lower()
        codes = load_codes()

        matched_event = get_event_by_code(content)
        if matched_event:
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            question_list = event_questions.get(matched_event.lower(), questions)
            question = random.choice(question_list)

            username = str(user)
            real_name = ID_MAP.get(str(user.id), "Unknown")

            self.awaiting_response[user.id] = {
                "username": username,
                "real_name": real_name,
                "timestamp": timestamp,
                "question": question,
                "event": matched_event
            }

            await user.send(
                f"✅ Thanks {real_name if real_name != 'Unknown' else username}! "
                f"Your attendance for **{matched_event}** has been recorded.\n\n"
                f"🧠 Quick question:\n**{question}**"
            )

        elif user.id in self.awaiting_response:
            data = self.awaiting_response.pop(user.id)
            answer = message.content.strip()
            row = [
                data["username"], data["real_name"], data["timestamp"],
                data["event"], data["question"], answer
            ]
            sheet.append_row(row)
            await user.send("📌 Thanks! Your response has been recorded.")
        else:
            await user.send("❌ Invalid code. Please try again with the correct attendance phrase.")

    # !setcode <eventname> <codename> - Command to set a new attendance code for an event via DM (ADMIN ONLY)
    @commands.command(name="setcode")
    async def set_attendance_code(self, ctx, event: str, *, new_code: str):
        # Check if the command is used in a DM
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("❌ This command can only be used in DMs.")
            return

        # Check if user has Admin role
        if not await self.is_admin(ctx):
            await ctx.send("⛔ You don't have permission to set attendance codes.")
            return

        # Save the code and confirm to the admin
        save_code(event, new_code)
        await ctx.send(f"✅ Code for event `{event}` set to: `{new_code.strip().lower()}`")

    # !removecode <eventname> - Command to remove an attendance code for an event via DM (ADMIN ONLY)
    @commands.command(name="removecode")
    async def remove_attendance_code(self, ctx, event: str):
        # Check if the command is used in a DM
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("❌ This command can only be used in DMs.")
            return

        # Check if user has Admin role
        if not await self.is_admin(ctx):
            await ctx.send("⛔ You don't have permission to remove attendance codes.")
            return

        # Load the existing codes
        codes = load_codes()
        event_key = event.lower()

        if event_key in codes:
            # Remove the event and save the updated dictionary
            del codes[event_key]
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["codes"] = codes
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            await ctx.send(f"🗑️ Code for `{event}` has been removed.")
        else:
            await ctx.send(f"⚠️ No code found for event `{event}`.")

    # !listcodes - Command to list all attendance codes via DM (ADMIN ONLY)
    @commands.command(name="listcodes")
    async def list_attendance_codes(self, ctx):
        # Check if the command is used in a DM
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("❌ This command can only be used in DMs.")
            return

        # Check if user has Admin role
        if not await self.is_admin(ctx):
            await ctx.send("⛔ You don't have permission to view the attendance codes.")
            return

        # Load and display all attendance codes
        codes = load_codes()
        if not codes:
            await ctx.send("⚠️ No attendance codes are currently set.")
            return

        message = "**📋 Attendance Codes:**\n"
        for event, code in codes.items():
            message += f"• `{event}` → `{code}`\n"

        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(Attendance(bot))
