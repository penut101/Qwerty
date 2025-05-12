import discord
from discord.ext import commands, tasks
import json
import random
from datetime import datetime, timedelta
import os
import calendar
from PIL import Image, ImageDraw, ImageFont

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
    #Set birthday command
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
    #Remove birthday command
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
    #Check birthday command
    async def mybirthday(self, ctx):
        """Check your set birthday."""
        user_id = str(ctx.author.id)
        birthdays = self.load_birthdays()
        if user_id in birthdays:
            await ctx.send(f"{ctx.author.mention}, your birthday is set to {birthdays[user_id]} 🎂")
        else:
            await ctx.send("You haven't set your birthday yet. Use `!setbirthday MM-DD` to do so.")

    @commands.command()
    async def birthdayboard(self, ctx):
        """Displays a calendar with member birthdays."""
        try:
            with open("birthdays.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            await ctx.send("🎂 No birthday data found.")
            return

        # Get current month and year
        now = datetime.now()
        year, month = now.year, now.month
        _, num_days = calendar.monthrange(year, month)

        # Build a map of day -> [usernames]
        day_birthdays = {day: [] for day in range(1, num_days + 1)}
        for user_id, bday in data.items():
            try:
                bday_month, bday_day = map(int, bday.split("-"))
                if bday_month == month:
                    user = await self.bot.fetch_user(int(user_id))
                    day_birthdays[bday_day].append(user.name)
            except Exception:
                continue

        # Image parameters
        width, height = 700, 500
        cell_w, cell_h = 100, 70
        font = ImageFont.truetype("arial.ttf", 14)

        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), f"{calendar.month_name[month]} {year}", fill="black", font=font)

        # Draw day headers
        for i, day_name in enumerate(calendar.day_abbr):
            draw.text((i * cell_w + 10, 40), day_name, fill="blue", font=font)

        # Draw calendar grid + birthdays
        first_weekday, _ = calendar.monthrange(year, month)
        day = 1
        y_offset = 60

        for week in range(6):
            for dow in range(7):
                x = dow * cell_w
                y = y_offset + week * cell_h
                if week == 0 and dow < first_weekday:
                    continue
                if day > num_days:
                    break

                draw.rectangle([x, y, x + cell_w, y + cell_h], outline="gray", width=1)
                draw.text((x + 5, y + 5), str(day), fill="black", font=font)

                # Add names for that day
                names = day_birthdays.get(day, [])
                for i, name in enumerate(names):
                    draw.text((x + 5, y + 20 + i * 14), name[:10], fill="green", font=font)

                day += 1

        # Save and send image
        img_path = "birthday_calendar.png"
        img.save(img_path)
        await ctx.send(file=discord.File(img_path))

    #Birthday check task
    @tasks.loop(time=datetime.strptime("08:00", "%H:%M").time()) # Check every day at 8 AM
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
