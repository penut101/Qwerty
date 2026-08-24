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
from discord import app_commands
import os
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz
import json
from dotenv import load_dotenv

from cogs.recruitment_common import is_main_member

# Load .env variables
load_dotenv()
SHEET_ID = os.getenv("SHEET_ID")

# Load name map (Discord ID → Real Name)
with open("name_map.json", "r", encoding="utf-8") as f:
    ID_MAP = json.load(f)

# Google Sheets setup
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
_sheet = None


def get_sheet():
    """Connect lazily so a temporary Sheets outage does not stop Qwerty startup."""
    global _sheet
    if _sheet is None:
        credentials_path = os.getenv(
            "MAIN_ATTENDANCE_CREDENTIALS", "qwerty-attendance-4f218a2cad1f.json"
        )
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_path, scope
        )
        client = gspread.authorize(credentials)
        _sheet = client.open_by_key(SHEET_ID).sheet1
    return _sheet

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
    "volunteer hours": ["How many hours did you volunteer for?"],
    "brotherhood event": [
        "1. Post Picture to Photo Circle: 1 point\n2. Attend a Rush Event as a Brother: 1 point \n3. Hanging out with KTP Brothers outside of Chapter: 1 point\n4. Going to KTP Social Event\n5. Attend Study Hours: 1 point\n6. Post KTP Related Content on Social Media (Reposting does not count): 1 point\n7. Wear KTP T-Shirt: 1 point\n8. Partake in Hackathon: 3 points"
    ],
    "networking event": [
        "1. Attend a fundraising Event: 1 point\n2. Attend a Philanthropy Event: 1 point\n3. Attend a Networking Event: 1 point\n4. Attending Career Fair: 1 point\n5. Help with recruitment/referring new brothers: 2 points",
    ],
    "chapter meeting": [
        "What are your plans for break?",
    ],
}


class MainAttendance(commands.Cog):
    # bot.py treats unmarked cogs as main-server-only for slash commands.
    guild_scope = "main"

    def __init__(self, bot):
        self.bot = bot
        self.awaiting_response = {}

    # Check staff permissions only in the server where the command was used.
    async def is_admin(self, interaction):
        member = interaction.user
        return isinstance(member, discord.Member) and (
            member.guild_permissions.manage_guild
            or any(role.name == "Admin" for role in member.roles)
        )

    # Listen for DMs to check attendance codes and log responses
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not isinstance(message.channel, discord.DMChannel):
            return
        if not is_main_member(message.author.id, self.bot):
            return

        user = message.author
        content = message.content.strip().lower()
        codes = load_codes()
        if content == "brotherhood":
            matched_event = "brotherhood event"
        else:
            matched_event = get_event_by_code(content)

        if content == "volunteer":
            matched_event = "volunteer hours"
        else:
            matched_event = get_event_by_code(content)
        if matched_event:
            # 🆕 Special case: Absent code
            if matched_event.lower() == "absent":
                # Ask the user why they will be absent
                await user.send(
                    "📝 I see you marked yourself as absent. Why will you be absent?"
                )

                # Store state so we know to expect a response
                self.awaiting_response[user.id] = {
                    "type": "absent",
                    "username": str(user),
                    "real_name": ID_MAP.get(str(user.id), "Unknown"),
                }
                return

            # ✅ Normal attendance handling
            eastern = pytz.timezone("US/Eastern")
            timestamp = datetime.now(eastern).strftime("%Y-%m-%d %H:%M:%S")
            question_list = event_questions.get(matched_event.lower(), questions)
            question = random.choice(question_list)

            username = str(user)
            real_name = ID_MAP.get(str(user.id), "Unknown")

            self.awaiting_response[user.id] = {
                "type": "attendance",
                "username": username,
                "real_name": real_name,
                "timestamp": timestamp,
                "question": question,
                "event": matched_event,
            }

            await user.send(
                f"✅ Thanks {real_name if real_name != 'Unknown' else username}! "
                f"Your attendance for **{matched_event}** has been recorded.\n\n"
                f"🧠 Quick question:\n**{question}**"
            )

        elif user.id in self.awaiting_response:
            data = self.awaiting_response.pop(user.id)
            if data["type"] == "absent":
                reason = message.content.strip()

                # Confirm to user
                await user.send("📌 Thanks! Your absence reason has been noted.")

                # Route reports to the current officer instead of a hard-coded person.
                admin_id = os.getenv("ABSENCE_ADMIN_USER_ID") or os.getenv("ABSENT_ID")
                if admin_id and admin_id.isdigit():
                    admin_user = await self.bot.fetch_user(int(admin_id))
                    await admin_user.send(
                        f"⚠️ {data['real_name'] if data['real_name'] != 'Unknown' else data['username']} "
                        f"reported ABSENT.\n\n📝 Reason: {reason}"
                    )
            else:
                # Handle normal attendance follow-up answer
                answer = message.content.strip()
                row = [
                    data["username"],
                    data["real_name"],
                    data["timestamp"],
                    data["event"],
                    data["question"],
                    answer,
                ]
                get_sheet().append_row(row)
                await user.send("📌 Thanks! Your response has been recorded.")
        else:
            # Another DM-based cog (such as recruitment attendance) may own it.
            return

    # Main-server attendance code management (admin only).
    @app_commands.describe(event="The event name", new_code="The new attendance code")
    @app_commands.command(
        name="setcode",
        description="Set a main-server attendance code (admin only)",
    )
    async def set_attendance_code(
        self, interaction: discord.Interaction, event: str, new_code: str
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Use this command in the main server.", ephemeral=True
            )
            return

        # Check if user has Admin role
        if not await self.is_admin(interaction):
            await interaction.response.send_message(
                "⛔ You don't have permission to set attendance codes.", ephemeral=True
            )
            return

        # Save the code and confirm to the admin
        save_code(event, new_code)
        await interaction.response.send_message(
            f"✅ Code for event `{event}` set to: `{new_code.strip().lower()}`",
            ephemeral=True,
        )

    # !removecode <eventname> - Command to remove an attendance code for an event via DM (ADMIN ONLY)
    @app_commands.describe(event="The event name to remove the code for")
    @app_commands.command(
        name="removecode",
        description="Remove a main-server attendance code (admin only)",
    )
    async def remove_attendance_code(
        self, interaction: discord.Interaction, event: str
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Use this command in the main server.", ephemeral=True
            )
            return

        # Check if user has Admin role
        if not await self.is_admin(interaction):
            await interaction.response.send_message(
                "⛔ You don't have permission to remove attendance codes.", ephemeral=True
            )
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

            await interaction.response.send_message(
                f"🗑️ Code for `{event}` has been removed.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"⚠️ No code found for event `{event}`.", ephemeral=True
            )

    # !listcodes - Command to list all attendance codes via DM (ADMIN ONLY)
    @app_commands.command(
        name="listcodes",
        description="List main-server attendance codes (admin only)",
    )
    async def list_attendance_codes(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Use this command in the main server.", ephemeral=True
            )
            return

        # Check if user has Admin role
        if not await self.is_admin(interaction):
            await interaction.response.send_message(
                "⛔ You don't have permission to view the attendance codes.", ephemeral=True
            )
            return

        # Load and display all attendance codes
        codes = load_codes()
        if not codes:
            await interaction.response.send_message(
                "⚠️ No attendance codes are currently set.", ephemeral=True
            )
            return

        message = "**📋 Attendance Codes:**\n"
        for event, code in codes.items():
            message += f"• `{event}` → `{code}`\n"

        await interaction.response.send_message(message, ephemeral=True)


async def setup(bot):
    await bot.add_cog(MainAttendance(bot))
