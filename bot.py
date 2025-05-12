import discord
from discord.ext import commands, tasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import json
import random
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
BIRTHDAY_CHANNEL_ID = int(os.getenv('BIRTHDAY_CHANNEL_ID'))

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
scheduler = AsyncIOScheduler()

# Load Birthday data from JSON file
def load_birthdays():
    try:
        with open('birthdays.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
#Save Birthday data to JSON file
def save_birthdays(data):
    with open('birthdays.json', 'w') as f:
        json.dump(data, f, indent=4)
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    scheduler.start()
    scheduler.add_job(check_birthdays, 'cron', hour=0, minute=0)
#Set your birthday
@bot.command()
async def setbirthday(ctx, date: str):
    """Set your birthday. Format: MM-DD"""
    try:
        datetime.strptime(date, "%m-%d")
        user_id = str(ctx.author.id)
        birthdays = load_birthdays()
        birthdays[user_id] = date
        save_birthdays(birthdays)
        await ctx.send(f"{ctx.author.mention}, your birthday has been set to {date} 🎉")
    except ValueError:
        await ctx.send("Invalid date format! Use MM-DD.")
#Renove your birthday
@bot.command()
async def removebirthday(ctx):
    """Remove your birthday from the records."""
    user_id = str(ctx.author.id)
    birthdays = load_birthdays()

    if user_id in birthdays:
        del birthdays[user_id]
        save_birthdays(birthdays)
        await ctx.send(f"{ctx.author.mention}, your birthday has been removed.")
    else:
        await ctx.send("You don't have a birthday set.")
#Check your birthday
@bot.command()
async def mybirthday(ctx):
    """Check your set birthday."""
    user_id = str(ctx.author.id)
    birthdays = load_birthdays()
    if user_id in birthdays:
        await ctx.send(f"{ctx.author.mention}, your birthday is set to {birthdays[user_id]} 🎂")
    else:
        await ctx.send("You haven't set your birthday yet. Use `!setbirthday MM-DD` to do so.")
#Send birthday messages
async def check_birthdays():
    today = datetime.now().strftime("%m-%d")
    birthdays = load_birthdays()
    channel = bot.get_channel(BIRTHDAY_CHANNEL_ID)

    birthday_messages = [
        "🎉 Happy Birthday, {mention}! 🎂 Wishing you a day full of cake and joy!",
        "🎈 {mention}, it's your special day! Have an amazing birthday! 🎁",
        "🥳 {mention}, happy birthday!! Hope your day is as awesome as you are!",
        "🎂 Wishing you the happiest of birthdays, {mention}! Celebrate big!",
        "🎊 {mention}, it’s birthday time! Enjoy every second of it!",
        "🌟 Happy B-Day, {mention}! May all your wishes come true!",
        "🍰 {mention}, sending you good vibes and sweet treats today!",
        "🎁 It’s party time for {mention}! Happy Birthday!!!",
        "🧁 Happy Birthday to the legend {mention}! Have a blast!",
        "✨ {mention}, cheers to another year of greatness! Happy Birthday!"
    ]

    for user_id, date in birthdays.items():
        if date == today:
            user = await bot.fetch_user(int(user_id))
            if user and channel:
                message = random.choice(birthday_messages).format(mention=user.mention)
                await channel.send(message)

bot.run(TOKEN)
