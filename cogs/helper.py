# This is a cog for the Qwerty Bot
# It contains helper commands that users can interact with.
# Written by Aiden Nemeroff

# Needed dependencies:
# discord.py
import discord
from discord.ext import commands

class HelperCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    # Get a list of commands
    async def help(self, ctx):
        """Display all bot commands organized by category."""
        help_message = (
            "**📌 General Commands:**\n"
            "`!mastersheet` - Get the link to the mastersheet\n"
            "`!library` - View the KTP Library\n"
            "`!eboard` - View the list of Eboard Members\n"
            "`!gboard` - View the list of Gboard Members\n\n"

            "**🎉 Birthday Commands:**\n"
            "`!setbirthday MM-DD` - Set your birthday\n"
            "`!removebirthday` - Remove your saved birthday\n"
            "`!mybirthday` - Check your current birthday\n"
            "`!birthdayboard` - View the birthday calendar\n\n"

            "**🎲 Fun Commands:**\n"
            "`!eightball <question>` - Ask the magic 8-ball a question\n"
            "`!fact` - Get a random fun fact\n"
            "`!vibecheck` - See if you pass the vibe check\n"
            "`!coinflip` - Flip a coin\n\n"
            "`!typefight <difficulty>` — Start a typing speed game. Difficulty levels: `easy`, `medium`, `hard`."
            "`!typefightleaderboard <difficulty>` — View the top TypeFight scorers per difficulty."
        )

        await ctx.send(f"{ctx.author.mention}, here’s everything I can do! 🧠\n```markdown\n{help_message}```")
        await ctx.send("If you need help with anything else, feel free to ask! 😊")


    @commands.command()
    # !mastersheet - Get the link to the mastersheet
    async def mastersheet(self, ctx):
        """Get the link to the mastersheet."""
        link = "https://docs.google.com/spreadsheets/d/1B6FqP82Z6yxfYrwbLGxEwBThZUMl6n1NnLL3TKbzCfo/edit?usp=sharing"
        await ctx.send(f"{ctx.author.mention}, here’s the link! 👉 {link} 🎉")

    @commands.command()
    # !eboard - Get the list of Eboard Members
    async def eboard(self, ctx):
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
        await ctx.send(f"{ctx.author.mention}, here’s the Eboard members! 👉\n```{eboard_list}```")

    @commands.command()
    # !gboard - Get the list of Gboard Members 
    async def gboard(self, ctx):
        """Get the list of Gboard Members."""
        gboard_list = (
            "Assistant Tech: Kylie Ridilla\n"
            "Merchandise: Katherine Lin\n"
            "Philanthropy: Chris Berarducci\n"
            "Alumni: Margo Brown\n"
            "Scholarship: Sumayyah Borders\n"
            "Assistant Recruitment: Kesley Hall\n"
            "New Member Ed: Mason Pavelik\n"
            "Brotherhood: Lexi Shainoff"
        )
        await ctx.send(f"{ctx.author.mention}, here’s the Gboard members! 👉\n```{gboard_list}```")

    @commands.command()
    # !library - View the KTP Library
    async def library(self, ctx):
        """View the KTP Library."""
        library_link = "https://drive.google.com/drive/folders/1VF71eiYQBZEFti79nTn-kPPwVyPdcKWb?usp=drive_link"
        await ctx.send(f"{ctx.author.mention}, here’s the Library Link! 👉\n``{library_link}``")

async def setup(bot):
    await bot.add_cog(HelperCog(bot))