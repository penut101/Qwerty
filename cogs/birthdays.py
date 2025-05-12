import discord
from discord.ext import commands, tasks
import json
import random
from datetime import datetime
import os

class BirthdayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_birthdays.start()

    def load_birthdays(self):
        try:
            with open('birthdays.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_birthdays(self, data):
        with open('birthdays.json', 'w') as f:
            json.dump(data, f, indent=4)

    @commands.command()
    async def setbirthday(self, ctx, date: str):
        """Set your birthday. Format: MM-DD"""
        try:
            datetime.strptime(date, "%m-%d")
            user_id = str(ctx.author.id)
            birthdays = self.load_birthdays()
            birthdays[user_id] = date
            self.save_birthdays(birthdays)
            await ctx.send(f"{ctx.author.mention}, your birthday has been set to {date} 🎉")
        except ValueError:
            await ctx.send("Invalid date format! Use MM-DD.")

    @commands.command()
    async def removebirthday(self, ctx):
        """Remove your birthday from the records."""
        user_id = str(ctx.author.id)
        birthdays = self.load_birthdays()

        if user_id in birthdays:
            del birthdays[user_id]
            self.save_birthdays(birthdays)
            await ctx.send(f"{ctx.author.mention}, your birthday has been removed.")
        else:
            await ctx.send("You don't have a birthday set.")

    @commands.command()
    async def mybirthday(self, ctx):
        """Check your set birthday."""
        user_id = str(ctx.author.id)
        birthdays = self.load_birthdays()
        if user_id in birthdays:
            await ctx.send(f"{ctx.author.mention}, your birthday is set to {birthdays[user_id]} 🎂")
        else:
            await ctx.send("You haven't set your birthday yet. Use `!setbirthday MM-DD` to do so.")

    @tasks.loop(time=datetime.strptime("08:00", "%H:%M").time())
    async def check_birthdays(self):
        today = datetime.now().strftime("%m-%d")
        birthdays = self.load_birthdays()
        channel = self.bot.get_channel(int(os.getenv('BIRTHDAY_CHANNEL_ID')))

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
                user = await self.bot.fetch_user(int(user_id))
                if user and channel:
                    message = random.choice(birthday_messages).format(mention=user.mention)
                    await channel.send(message)

async def setup(bot):
    await bot.add_cog(BirthdayCog(bot))
