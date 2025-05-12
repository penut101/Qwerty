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
    print(f'✅ Bot is ready! Logged in as {bot.user}.')

async def main():
    await bot.load_extension("cogs.birthdays")
    await bot.load_extension("cogs.roles")
    await bot.load_extension("cogs.helper")
    await bot.start(TOKEN)

asyncio.run(main())
