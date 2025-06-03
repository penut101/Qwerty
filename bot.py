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

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    # This event is called when the bot is ready and has logged in successfully.
    print(f'✅ Bot is ready! Logged in as {bot.user}.')


# This is where we load the cogs for the bot. Each cog contains a specific functionality.
async def main():
    await bot.load_extension("cogs.birthdays")
    await bot.load_extension("cogs.roles")
    await bot.load_extension("cogs.helper")
    await bot.load_extension("cogs.fun")
    await bot.load_extension("cogs.attendance")
    await bot.load_extension("cogs.export_members")
    await bot.start(TOKEN)

asyncio.run(main())
