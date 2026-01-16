# This is a cog for the Qwerty Bot
# It contains helper commands that users can interact with.
# Written by Aiden Nemeroff

# Needed dependencies:
# discord.py
import discord
from discord.ext import commands
from discord import app_commands


class HelperCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Display all bot commands organized by category")
    # Get a list of commands
    async def help(self, interaction: discord.Interaction):
        """Display all bot commands organized by category."""
        help_message = (
            "**📌 General Commands:**\n"
            "`/mastersheet` - Get the link to the mastersheet\n"
            "`/library` - View the KTP Library\n"
            "`/eboard` - View the list of Eboard Members\n"
            "`/gboard` - View the list of Gboard Members\n\n"
            "`/photocircle` - Get the link to the Photo Circle\n\n"
            "**🎉 Birthday Commands:**\n"
            "`/setbirthday MM-DD` - Set your birthday\n"
            "`/removebirthday` - Remove your saved birthday\n"
            "`/mybirthday` - Check your current birthday\n"
            "`/birthdayboard` - View the birthday calendar\n\n"
            "**🎲 Fun Commands:**\n"
            "`/eightball <question>` - Ask the magic 8-ball a question\n"
            "`/fact` - Get a random fun fact\n"
            "`/vibecheck` - See if you pass the vibe check\n"
            "`/coinflip` - Flip a coin\n\n"
            "`/typefight <difficulty>` — Start a typing speed game. Difficulty levels: `easy`, `medium`, `hard`."
            "`/typefightleaderboard <difficulty>` — View the top TypeFight scorers per difficulty."
            "`/hangman` — Start a game of Hangman.\n"
            "`/guess <letter>` — Guess a letter in Hangman.\n"
            "`/solve <word>` — Attempt to solve the Hangman puzzle.\n"
            "`/hangmanscoreboard` — View the Hangman leaderboard.\n"
        )

        await interaction.response.send_message(
            f"{interaction.user.mention}, here’s everything I can do! 🧠\n```markdown\n{help_message}```"
        )
        await interaction.followup.send("If you need help with anything else, feel free to ask! 😊")

    @app_commands.command(name="mastersheet", description="Get the link to the mastersheet")
    # !mastersheet - Get the link to the mastersheet
    async def mastersheet(self, interaction: discord.Interaction):
        """Get the link to the mastersheet."""
        link = "https://docs.google.com/spreadsheets/d/1B6FqP82Z6yxfYrwbLGxEwBThZUMl6n1NnLL3TKbzCfo/edit?usp=sharing"
        await interaction.response.send_message(f"{interaction.user.mention}, here’s the link! 👉 {link} 🎉")

    @app_commands.command(name="eboard", description="Get the list of Eboard Members")
    # !eboard - Get the list of Eboard Members
    async def eboard(self, interaction: discord.Interaction):
        """Get the list of Eboard Members."""
        eboard_list = (
            "President: Connor Reger\n"
            "VP of External Affairs: Pearl Singer\n"
            "VP of Finance: Jacob Wong\n"
            "VP of Tech Dev: Aiden Nemeroff\n"
            "VP of Membership: Will Huynh\n"
            "VP of Internal Affairs: Jess Wagner\n"
            "VP of Social Engagement: Nathan Sloan\n"
            "VP of Professional Development: Diana Lysova\n"
            "VP of Marketing: Hunter Foster\n"
            "VP of DEIB: Mike Puthumana"
        )
        await interaction.response.send_message(
            f"{interaction.user.mention}, here’s the Eboard members! 👉\n```{eboard_list}```"
        )

    @app_commands.command(name="gboard", description="Get the list of Gboard Members")
    # !gboard - Get the list of Gboard Members
    async def gboard(self, interaction: discord.Interaction):
        """Get the list of Gboard Members."""
        gboard_list = (
            "Assistant Tech: Kylie Ridilla\n"
            "Merchandise: Katherine Lin\n"
            "Philanthropy: Chris Berarducci\n"
            "Alumni: Margo Brown\n"
            "Scholarship: Sumayyah Borders\n"
            "Assistant Recruitment: Kelsey Hall\n"
            "New Member Ed: Mason Pavelik\n"
            "Brotherhood: Lexi Shainoff"
        )
        await interaction.response.send_message(
            f"{interaction.user.mention}, here’s the Gboard members! 👉\n```{gboard_list}```"
        )

    @app_commands.command(name="library", description="View the KTP Library")
    # !library - View the KTP Library
    async def library(self, interaction: discord.Interaction):
        """View the KTP Library."""
        library_link = "https://drive.google.com/drive/folders/1VF71eiYQBZEFti79nTn-kPPwVyPdcKWb?usp=drive_link"
        await interaction.response.send_message(
            f"{interaction.user.mention}, here’s the Library Link! 👉\n``{library_link}``"
        )

    # !photocircle - Get the link to the Photo Circle.
    @app_commands.command(name="photocircle", description="Get the link to the Photo Circle")
    async def photocircle(self, interaction: discord.Interaction):
        """Get the link to the Photo Circle."""
        photocircle_link = "https://join.photocircleapp.com/7CS260R3FA"
        await interaction.response.send_message(
            f"{interaction.user.mention}, here’s the Photo Circle Link! 👉\n``{photocircle_link}``"
        )


async def setup(bot):
    await bot.add_cog(HelperCog(bot))
