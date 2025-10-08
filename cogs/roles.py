# This is a cog for the Qwerty Bot
# It contains role management commands that users can interact with.
# The bot allows users to set up reaction roles, where users can react to a message to get a role.
# Written by Aiden Nemeroff

# Needed dependencies:
# discord.py
import discord
from discord.ext import commands
import os
import asyncio

# List of roles and their corresponding emojis
# List of roles and their corresponding emojis
reaction_roles = {
    "🎮": "Gamer",
    "🎵": "Music",
    "🧗": "Rock Climbing",
    "🍔": "Foodie",
    "🏋️‍♂️": "Gym",
    "🎱": "Pool",
    "🏓": "Ping Pong",
    "🌈": "LGBTQ+",
    "💻": "Computer Science",
    "📊": "Information Science",
    "🧬": "Computational Biology",
    "🎨": "Digital Interactive & Design",
    "📈": "Data Science",
    "⚛️": "Physics and Quantum Computing",
    "💵": "Economics",
    "📚": "English Literature",
    "🖥️": "Computer Engineering",
    "➗": "Mathematics",
}


class RolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    # !setuproles - Post a message for users to get roles via reactions (Admin only)
    async def setuproles(self, ctx):
        """Post the reaction role message."""
        msg = await ctx.send(
            "React to get a role:\n"
            "🎮 = Gamer\n"
            "🎵 = Music\n"
            "🧗 = Rock Climbing\n"
            "🍔 = Foodie\n"
            "🏋️‍♂️ = Gym\n"
            "🎱 = Pool\n"
            "🏓 = Ping Pong\n"
            "🌈 = LGBTQ+\n"
            "💻 = Computer Science\n"
            "📊 = Information Science\n"
            "🧬 = Computational Biology\n"
            "🎨 = Digital Interactive & Design\n"
            "📈 = Data Science\n"
            "⚛️ = Physics and Quantum Computing\n"
            "💵 = Economics\n"
            "📚 = English Literature\n"
            "🖥️ = Computer Engineering\n"
            "➗ = Mathematics"
        )
        # Add reactions to the message for each role
        for emoji in reaction_roles:
            await msg.add_reaction(emoji)

        # Save the message ID to a file for later reference
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

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setupmajorroles(self, ctx):
        """Create all major roles and add them to reaction_roles (Admin only)."""
        majors_with_emojis = {
            "💻": "Computer Science",
            "📊": "Information Science",
            "🧬": "Computational Biology",
            "🎨": "Digital Interactive & Design",
            "📈": "Data Science",
            "⚛️": "Physics and Quantum Computing",
            "💵": "Economics",
            "📚": "English Literature",
            "🖥️": "Computer Engineering",
            "➗": "Mathematics",
        }

        guild = ctx.guild
        created = []
        already = []

        # Ensure majors exist as roles
        for emoji, major in majors_with_emojis.items():
            role = discord.utils.get(guild.roles, name=major)
            if role is None:
                await guild.create_role(name=major)
                created.append(major)
            else:
                already.append(major)

            # Update global reaction_roles dict
            if emoji not in reaction_roles:
                reaction_roles[emoji] = major

        msg = ""
        if created:
            msg += f"✅ Created roles: {', '.join(created)}\n"
        if already:
            msg += f"ℹ️ Already existing: {', '.join(already)}\n"
        msg += "📌 Majors added to reaction roles for `!setuproles`."
        await ctx.send(msg)


async def setup(bot):
    await bot.add_cog(RolesCog(bot))
