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
        # Load QWERTY logo
        logo_path = "QWERTY Bot Logo.png"  # Make sure this is in your bot's directory
        logo = Image.open(logo_path).convert("RGBA").resize((150, 150))

        # Setup image
        width, height = 715, 590
        cell_w, cell_h = 100, 75
        padding_top = 160

        bg_color = "#006b8f"
        title_color = "#f6ec6b"
        tile_color = "#ffffff"
        text_color = "#333"
        bday_color = "#3498DB"

        try:
            font_title = ImageFont.truetype("fira.ttf", 32)
            font_day = ImageFont.truetype("fira.ttf", 20)
            font_name = ImageFont.truetype("fira.ttf", 16)
        except:
            font_title = ImageFont.load_default()
            font_day = ImageFont.load_default()
            font_name = ImageFont.load_default()

        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # Logo and title
        img.paste(logo, ((width - logo.width) // 2, 5), logo)
        title = f"{calendar.month_name[month]} {year} Birthday Board"
        draw.text(((width - draw.textlength(title, font=font_title)) // 2, 160), title, fill=title_color, font=font_title)

        # Weekday headers
        for i, day_name in enumerate(calendar.day_abbr):
            draw.text((i * cell_w + 30, padding_top + 20), day_name, fill="white", font=font_day)

        first_weekday, _ = calendar.monthrange(year, month)
        day = 1
        y_start = padding_top + 40

        for week in range(6):
            for dow in range(7):
                x = dow * cell_w
                y = y_start + week * cell_h
                if week == 0 and dow < first_weekday:
                    continue
                if day > num_days:
                    break

                draw.rounded_rectangle([x + 5, y + 5, x + cell_w - 5, y + cell_h - 5], radius=10, fill=tile_color, outline="#dddddd")
                draw.text((x + 10, y + 8), str(day), fill=text_color, font=font_day)

                for i, name in enumerate(day_birthdays.get(day, [])):
                    draw.text((x + 10, y + 25 + i * 15), f"🎂 {name[:12]}", fill=bday_color, font=font_name)

                day += 1

        # Save and send
        out_path = f"birthday_board_{month}.png"
        img.save(out_path)
        await ctx.send(file=discord.File(out_path))
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
