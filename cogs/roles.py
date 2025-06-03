# This is a cog for the Qwerty Bot
# It contains role management commands that users can interact with.
# The bot allows users to set up reaction roles, where users can react to a message to get a role.
# Written by Aiden Nemeroff

# Needed dependencies:
# discord.py
import discord
from discord.ext import commands
import os

#List of roles and their corresponding emojis
reaction_roles = {
    "🎮": "Gamer",
    "🎵": "Music",
    "🧗": "Rock Climbing",
    "🍔": "Foodie"
}

class RolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    #!setuproles - Post a message for users to get roles via reactions (Admin only)
    async def setuproles(self, ctx):
        """Post the reaction role message."""
        msg = await ctx.send(
            "React to get a role:\n"
            "🎮 = Gamer\n"
            "🎵 = Music\n"
            "🧗 = Rock Climbing\n"
            "🍔 = Foodie"
        )
        for emoji in reaction_roles:
            await msg.add_reaction(emoji)

        with open("reaction_roles_msg.txt", "w") as f:
            f.write(str(msg.id))

    @commands.Cog.listener()
    # Listen for reactions to the message
    async def on_raw_reaction_add(self, payload):
        if payload.member and payload.member.bot:
            return

        try:
            with open("reaction_roles_msg.txt", "r") as f:
                target_message_id = int(f.read())
        except FileNotFoundError:
            return

        if payload.message_id != target_message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        role_name = reaction_roles.get(str(payload.emoji.name))
        if role_name:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                await payload.member.add_roles(role)

    @commands.Cog.listener()
    # Listen for reaction removal from the message
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)

        try:
            with open("reaction_roles_msg.txt", "r") as f:
                target_message_id = int(f.read())
        except FileNotFoundError:
            return

        if payload.message_id != target_message_id:
            return

        role_name = reaction_roles.get(str(payload.emoji.name))
        if role_name:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                await member.remove_roles(role)

async def setup(bot):
    await bot.add_cog(RolesCog(bot))
