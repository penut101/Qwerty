# This is a cog for the Qwerty Bot
# It contains birthday management commands that users can interact with.
# Written by Aiden Nemeroff

import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import random
from datetime import datetime, time
import pytz
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
        """Try bundled fira.ttf, then system fonts, then default."""
        try:
            # First try bundled font
            font_path = Path(__file__).resolve().parent.parent / "fira.ttf"
            if font_path.exists():
                return ImageFont.truetype(str(font_path), size)

            # Try system fonts on Windows
            if os.name == "nt":
                windows_font = "arial.ttf"
                system_font_path = os.path.join(
                    os.environ["WINDIR"], "Fonts", windows_font
                )
                if os.path.exists(system_font_path):
                    return ImageFont.truetype(system_font_path, size)

            # Try system fonts on Linux
            linux_fonts = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/firacode/FiraCode-Regular.ttf",
            ]
            for path in linux_fonts:
                if Path(path).exists():
                    return ImageFont.truetype(path, size)
        except Exception as e:
            print(f"Font loading error: {e}")

        return ImageFont.load_default()

    # ---------------- Commands ----------------
    @app_commands.describe(date="The birthday date in MM-DD format")
    @app_commands.command(name="setbirthday", description="Set your birthday")
    async def setbirthday(self, interaction: discord.Interaction, date: str):
        """Set your birthday"""
        try:
            datetime.strptime(date, "%m-%d")
            user_id = str(interaction.user.id)
            birthdays = self.load_birthdays()
            birthdays[user_id] = date
            self.save_birthdays(birthdays)
            await interaction.response.send_message(
                f"{interaction.user.mention}, your birthday has been set to {date} 🎉"
            )
        except ValueError:
            await interaction.response.send_message("Invalid date format! Use MM-DD.")

    @app_commands.command(name="removebirthday", description="Remove your saved birthday")
    async def removebirthday(self, interaction: discord.Interaction):
        """Remove your birthday"""
        user_id = str(interaction.user.id)
        birthdays = self.load_birthdays()
        if user_id in birthdays:
            del birthdays[user_id]
            self.save_birthdays(birthdays)
            await interaction.response.send_message(f"{interaction.user.mention}, your birthday has been removed.")
        else:
            await interaction.response.send_message("You don't have a birthday set.")

    @app_commands.command(name="mybirthday", description="Check your current birthday")
    async def mybirthday(self, interaction: discord.Interaction):
        """Check your birthday"""
        user_id = str(interaction.user.id)
        birthdays = self.load_birthdays()
        if user_id in birthdays:
            await interaction.response.send_message(
                f"{interaction.user.mention}, your birthday is set to {birthdays[user_id]} 🎂"
            )
        else:
            await interaction.response.send_message(
                "You haven't set your birthday yet. Use `/setbirthday MM-DD`."
            )

    # ---------------- Birthday Board ----------------
    @app_commands.command(name="birthdayboard", description="View the birthday calendar")
    async def birthdayboard(self, interaction: discord.Interaction):
        """Displays a calendar with member birthdays"""
        try:
            with open("birthdays.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            await interaction.response.send_message("🎂 No birthday data found.")
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
            member = interaction.guild.get_member(uid)
            if member:
                name = member.display_name
            else:
                try:
                    member = await interaction.guild.fetch_member(uid)
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

            # Use our custom font loader for all fonts
            font_title = self.load_font(30)
            font_day = self.load_font(20)
            font_name = self.load_font(16)

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
            await interaction.response.send_message(file=discord.File(out_path))
            return

        except Exception as e:
            await interaction.response.send_message(f"⚠️ Could not generate image: {e}")

    # ---------------- Daily Birthday Checker ----------------
    @tasks.loop(
        time=time(12, 0, tzinfo=pytz.timezone("US/Eastern"))
    )  # 12:00 PM Eastern
    async def check_birthdays(self):
        eastern = pytz.timezone("US/Eastern")
        today = datetime.now(eastern).strftime("%m-%d")
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

    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(BirthdayCog(bot))
