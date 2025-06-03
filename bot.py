# Driver code for the Qwerty Bot
# Written by Aiden Nemeroff
# This file is the main driver code for the Qwerty Bot, a Discord bot that provides various functionalities including birthday management, role management, and fun commands.
# The bot is built using the discord.py library and is designed to be modular, with different functionalities separated into cogs.

# Needed dependencies:
# requrements.txt
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
# This is the Discord bot token, which is used to authenticate the bot with the Discord API.
# Make sure to set this in your .env file or environment variables.
TOKEN = os.getenv('DISCORD_TOKEN')

# This is the intents for the bot. Intents are used to specify which events the bot should receive from Discord.
# For example, if the bot needs to receive messages, it should have the message_content intent enabled.
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
intents.guilds = True

# This is the main bot instance. The command_prefix is set to '!', which means users can invoke commands with a '!' prefix.
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    # This event is called when the bot is ready and has logged in successfully.
    print(f'✅ Bot is ready! Logged in as {bot.user}.')


# This is where we load the cogs for the bot. Each cog contains a specific functionality. 
# There is a print statement for each cog to indicate successful loading.
async def main():
    await bot.load_extension("cogs.birthdays")
    print("✅ Loaded Birthdays Cog")
    await bot.load_extension("cogs.roles")
    print("✅ Loaded Roles Cog")
    await bot.load_extension("cogs.helper")
    print("✅ Loaded Helper Cog")
    await bot.load_extension("cogs.fun")
    print("✅ Loaded Fun Cog")
    await bot.load_extension("cogs.attendance")
    print("✅ Loaded Attendance Cog")
    await bot.load_extension("cogs.export_members")
    print("✅ Loaded Export Members Cog")
    await bot.start(TOKEN)

asyncio.run(main())
