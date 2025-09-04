# This is a cog for the Qwerty Bot
# It contains birthday management commands that users can interact with.
# Written by Aiden Nemeroff

import discord
from discord.ext import commands, tasks
import json
import random
from datetime import datetime
import os
import calendar
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


class BirthdayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_birthdays.start()

    # ---------------- Utility: JSON ----------------
    def load_birthdays(self):
        try:
            with open("birthdays.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_birthdays(self, data):
        with open("birthdays.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # ---------------- Utility: Font ----------------
    def load_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Try system Fira, then bundled fira.ttf, then default."""
        candidates = [
            "/usr/share/fonts/truetype/firacode/FiraCode-Regular.ttf",  # apt install fonts-firacode
            str(
                Path(__file__).resolve().parent.parent / "fira.ttf"
            ),  # bundled font in project root
        ]
        for path in candidates:
            if Path(path).exists():
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue
        return ImageFont.load_default()

    # ---------------- Commands ----------------
    @commands.command()
    async def setbirthday(self, ctx, date: str):
        """!setbirthday MM-DD - Set your birthday"""
        try:
            datetime.strptime(date, "%m-%d")
            user_id = str(ctx.author.id)
            birthdays = self.load_birthdays()
            birthdays[user_id] = date
            self.save_birthdays(birthdays)
            await ctx.send(
                f"{ctx.author.mention}, your birthday has been set to {date} 🎉"
            )
        except ValueError:
            await ctx.send("Invalid date format! Use MM-DD.")

    @commands.command()
    async def removebirthday(self, ctx):
        """!removebirthday - Remove your birthday"""
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
        """!mybirthday - Check your birthday"""
        user_id = str(ctx.author.id)
        birthdays = self.load_birthdays()
        if user_id in birthdays:
            await ctx.send(
                f"{ctx.author.mention}, your birthday is set to {birthdays[user_id]} 🎂"
            )
        else:
            await ctx.send(
                "You haven't set your birthday yet. Use `!setbirthday MM-DD`."
            )

    # ---------------- Birthday Board ----------------
    @commands.command()
    async def birthdayboard(self, ctx):
        """!birthdayboard - Displays a calendar with member birthdays"""
        try:
            with open("birthdays.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            await ctx.send("🎂 No birthday data found.")
            return

        now = datetime.now()
        year, month = now.year, now.month
        _, num_days = calendar.monthrange(year, month)
        day_birthdays = {d: [] for d in range(1, num_days + 1)}

        # Collect names
        for user_id, bday in data.items():
            try:
                bmonth, bday_num = map(int, bday.split("-"))
            except Exception:
                continue
            if bmonth != month:
                continue
            uid = int(user_id)
            name = None
            member = ctx.guild.get_member(uid)
            if member:
                name = member.display_name
            else:
                try:
                    member = await ctx.guild.fetch_member(uid)
                    name = member.display_name
                except Exception:
                    try:
                        user = await self.bot.fetch_user(uid)
                        name = getattr(user, "display_name", None) or user.name
                    except Exception:
                        name = f"Unknown ({user_id})"
            day_birthdays[bday_num].append(name)

        # Build the image
        try:
            here = Path(__file__).resolve().parent.parent
            logo_path = here / "QWERTY Bot Logo.png"
            logo = None
            if logo_path.exists():
                try:
                    logo = Image.open(str(logo_path)).convert("RGBA").resize((150, 150))
                except Exception:
                    logo = None

            width, height = 715, 590
            cell_w, cell_h = 100, 75
            padding_top = 160
            bg_color = "#006b8f"
            title_color = "#f6ec6b"
            tile_color = "#ffffff"
            text_color = "#333333"
            bday_color = "#3498DB"

            font_title = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30
            )
            font_day = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20
            )
            font_name = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16
            )

            img = Image.new("RGB", (width, height), bg_color)
            draw = ImageDraw.Draw(img)

            if logo:
                img.paste(logo, ((width - logo.width) // 2, 5), logo)

            title = f"{calendar.month_name[month]} {year} Birthday Board"
            try:
                title_w = draw.textlength(title, font=font_title)
            except AttributeError:
                bbox = draw.textbbox((0, 0), title, font=font_title)
                title_w = bbox[2] - bbox[0]
            title_x = (width - title_w) // 2
            draw.text((title_x, 160), title, fill=title_color, font=font_title)

            # Weekday headers
            for i, day_name in enumerate(calendar.day_abbr):
                draw.text(
                    (i * cell_w + 30, padding_top + 20),
                    day_name,
                    fill="white",
                    font=font_day,
                )

            # Calendar grid
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
                    draw.rounded_rectangle(
                        [x + 5, y + 5, x + cell_w - 5, y + cell_h - 5],
                        radius=10,
                        fill=tile_color,
                        outline="#dddddd",
                    )
                    draw.text((x + 10, y + 8), str(day), fill=text_color, font=font_day)
                    if day_birthdays.get(day):
                        for i, name in enumerate(day_birthdays[day][:3]):
                            draw.text(
                                (x + 10, y + 25 + i * 15),
                                f"🎂 {name[:20]}",
                                fill=bday_color,
                                font=font_name,
                            )
                    day += 1

            out_path = f"birthday_board_{month}.png"
            img.save(out_path)
            await ctx.send(file=discord.File(out_path))
            return

        except Exception as e:
            await ctx.send(f"⚠️ Could not generate image: {e}")

    # ---------------- Daily Birthday Checker ----------------
    @tasks.loop(
        time=datetime.strptime("12:00", "%H:%M").time()
    )  # Runs at 8am EST (12pm UTC)
    async def check_birthdays(self):
        today = datetime.now().strftime("%m-%d")
        birthdays = self.load_birthdays()
        channel = self.bot.get_channel(int(os.getenv("BIRTHDAY_CHANNEL_ID")))
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
            "✨ {mention}, cheers to another year of greatness! Happy Birthday!",
        ]
        for user_id, date in birthdays.items():
            if date == today:
                user = await self.bot.fetch_user(int(user_id))
                if user and channel:
                    msg = random.choice(birthday_messages).format(mention=user.mention)
                    await channel.send(msg)


async def setup(bot):
    await bot.add_cog(BirthdayCog(bot))
