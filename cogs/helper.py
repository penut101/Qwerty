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

            "**📌 Role Commands:**\n"
            "`!setuproles` - (Admin) Post a message for users to get roles via reactions\n"
        )

        await ctx.send(f"{ctx.author.mention}, here’s everything I can do! 🧠\n```markdown\n{help_message}```")
        await ctx.send("If you need help with anything else, feel free to ask! 😊")


    @commands.command()
    # Get the link to the mastersheet
    async def mastersheet(self, ctx):
        """Get the link to the mastersheet."""
        link = "https://docs.google.com/spreadsheets/d/1m84Ayqyl1vF-2EMA6lk7Quf_xFqOw19T04egipTGN70/edit?gid=0#gid=0"
        await ctx.send(f"{ctx.author.mention}, here’s the link! 👉 {link} 🎉")

    @commands.command()
    # Get the list of Eboard Members
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
    # Get the list of Gboard Members 
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

async def setup(bot):
    await bot.add_cog(HelperCog(bot))