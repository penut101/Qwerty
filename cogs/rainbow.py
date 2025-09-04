## This is a cog for the Qwerty Bot
# It contains commands to create rainbow roles and allow users with the LGBTQ+ role to cycle through rainbow colors.
# Written by Aiden Nemeroff

import asyncio
import discord
from discord.ext import commands


class RainbowRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # role names mapped to hex color values
        self.rainbow_roles = {
            "Red": 0xFF0000,
            "Orange": 0xFFA500,
            "Yellow": 0xFFFF00,
            "Green": 0x00FF00,
            "Blue": 0x0000FF,
            "Purple": 0x800080,
        }
        self.active_users = {}  # track who is running rainbow

    def has_lgbtq_role(self, member):
        """Check if a member has the LGBTQ+ role."""
        return discord.utils.get(member.roles, name="LGBTQ+") is not None

    #!createrainbowroles - Create rainbow roles command (admin only)
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def createrainbowroles(self, ctx):
        """Create rainbow roles if they don't exist."""
        guild = ctx.guild
        created = []
        for role_name, color_value in self.rainbow_roles.items():
            existing = discord.utils.get(guild.roles, name=role_name)
            if not existing:
                await guild.create_role(
                    name=role_name, colour=discord.Colour(color_value)
                )
                created.append(role_name)
        if created:
            await ctx.send(f"🌈 Created roles: {', '.join(created)}")
        else:
            await ctx.send("✅ All rainbow roles already exist!")

    #!startrainbow - Start rainbow cycling for yourself (must have LGBTQ+ role)
    @commands.command()
    async def startrainbow(self, ctx):
        """Start rainbow cycling for yourself (must have LGBTQ+ role)."""
        member = ctx.author

        if not self.has_lgbtq_role(member):
            await ctx.send("❌ You must have the LGBTQ+ role to use this command.")
            return

        if self.active_users.get(member.id, False):
            await ctx.send("🌈 Your rainbow cycle is already running!")
            return

        self.active_users[member.id] = True
        await ctx.send(f"🌈 {member.display_name}, your rainbow cycle has started!")

        while self.active_users.get(member.id, False):
            if not self.has_lgbtq_role(member):
                self.active_users[member.id] = False
                await ctx.send(
                    f"❌ {member.display_name}, your rainbow stopped (LGBTQ+ role removed)."
                )
                break

            for role_name in self.rainbow_roles:
                if not self.active_users.get(member.id, False):
                    break  # stop if user disabled
                role = discord.utils.get(ctx.guild.roles, name=role_name)
                if role:
                    # remove old rainbow roles
                    roles_to_remove = [
                        r for r in member.roles if r.name in self.rainbow_roles
                    ]
                    if roles_to_remove:
                        await member.remove_roles(*roles_to_remove)
                    # add the new color
                    await member.add_roles(role)
                await asyncio.sleep(2)  # change every 2 seconds

    #!stoprainbow - Stop your personal rainbow cycle
    @commands.command()
    async def stoprainbow(self, ctx):
        """Stop your personal rainbow cycle."""
        member = ctx.author
        if not self.active_users.get(member.id, False):
            await ctx.send("❌ You don’t have a rainbow cycle running.")
            return

        self.active_users[member.id] = False
        await ctx.send(
            f"🌈 {member.display_name}, your rainbow cycle has been stopped."
        )

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Stop rainbow if LGBTQ+ role is removed."""
        if self.active_users.get(after.id, False):
            had_lgbtq = discord.utils.get(before.roles, name="LGBTQ+")
            has_lgbtq = discord.utils.get(after.roles, name="LGBTQ+")
            if had_lgbtq and not has_lgbtq:
                self.active_users[after.id] = False
                # also clean rainbow roles from the member
                roles_to_remove = [
                    r for r in after.roles if r.name in self.rainbow_roles
                ]
                if roles_to_remove:
                    await after.remove_roles(*roles_to_remove)

    @commands.Cog.listener()
    async def on_ready(self): 
        """Failsafe: clear all rainbow states when bot restarts."""
        if self.active_users:
            self.active_users.clear()
        print("🌈 Rainbow role states reset on startup.")


async def setup(bot):
    await bot.add_cog(RainbowRoles(bot))
