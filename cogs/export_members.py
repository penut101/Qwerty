#
import discord
from discord.ext import commands
import json

class ExportMembers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="export_realnames")
    @commands.is_owner()
    async def export_realnames(self, ctx):
        guild = ctx.guild
        name_map = {str(member.id): member.display_name for member in guild.members if not member.bot}

        with open("name_map.json", "w", encoding="utf-8") as f:
            json.dump(name_map, f, indent=4)

        await ctx.send("✅ Exported member names to `name_map.json`.")

async def setup(bot):
    await bot.add_cog(ExportMembers(bot))
