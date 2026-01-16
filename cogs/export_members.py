# This is a cog for the Qwerty Bot
# It contains a quick command to export member names from the server to a JSON file.
# It is intended for use by the bot owner to create a mapping of user IDs to their display names.
# Written by Aiden Nemeroff

# Needed dependencies:
# discord.py
import discord
from discord.ext import commands
from discord import app_commands
import json

class ExportMembers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # !export_realnames - Command to export member names to a JSON file (bot owner only)
    @app_commands.command(name="export_realnames", description="Export member names to a JSON file (bot owner only)")
    async def export_realnames(self, interaction: discord.Interaction):
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message("You are not authorized to use this command.")
            return
        guild = interaction.guild # Get the guild (server) where the command was invoked
        name_map = {str(member.id): member.display_name for member in guild.members if not member.bot}   # Create a dictionary mapping user IDs to display names, excluding bots
        
        # Save the name map to a JSON file
        # This file will be created in the same directory as the script
        with open("name_map.json", "w", encoding="utf-8") as f:
            json.dump(name_map, f, indent=4)
        # Notify the user that the export was successful
        await interaction.response.send_message("✅ Exported member names to `name_map.json`.")

async def setup(bot):
    await bot.add_cog(ExportMembers(bot))
