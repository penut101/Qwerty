"""Qwerty entry point for the main and recruitment Discord servers.

One Discord application and token serves both guilds. Slash commands are
registered directly to the appropriate guild so members see only the commands
that belong in their server.
"""

from __future__ import annotations

import asyncio
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from cogs.recruitment_common import RECRUITMENT_SCOPE, guild_id


load_dotenv()

# Member access is needed to select PNMs, detect main-server joins, and assign
# the transition role. Message content is needed for attendance codewords in DMs.
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Qwerty's curated `/help` replaces discord.py's generic `!help` command.
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Existing community features remain available only in the main server.
MAIN_COGS = (
    "cogs.birthdays",
    "cogs.main_attendance",
    "cogs.roles",
    "cogs.helper",
    "cogs.fun",
    "cogs.typefight",
    "cogs.wordscramble",
    "cogs.hangman",
    "cogs.export_members",
    "cogs.rainbow",
)

# The focused recruitment toolset is available only in the recruitment server.
RECRUITMENT_COGS = (
    "cogs.pnm_verification",
    "cogs.recruitment_information",
    "cogs.recruitment_calendar",
    "cogs.recruitment_attendance",
    "cogs.anonymous_questions",
    "cogs.member_transition",
)


def validate_configuration() -> tuple[str, int, int]:
    """Fail early with a useful setup error instead of connecting half-ready."""
    token = os.getenv("DISCORD_TOKEN", "").strip()
    main_id = guild_id("MAIN_GUILD_ID")
    recruitment_id = guild_id("RECRUITMENT_GUILD_ID")
    missing = []
    if not token:
        missing.append("DISCORD_TOKEN")
    if main_id is None:
        missing.append("MAIN_GUILD_ID")
    if recruitment_id is None:
        missing.append("RECRUITMENT_GUILD_ID")
    if missing:
        raise RuntimeError(
            f"Missing required configuration: {', '.join(missing)}. See .env.example."
        )
    if main_id == recruitment_id:
        raise RuntimeError("MAIN_GUILD_ID and RECRUITMENT_GUILD_ID must be different.")
    return token, main_id, recruitment_id


def arrange_slash_commands(main_id: int, recruitment_id: int) -> None:
    """Move commands from the global registry into the correct guild registry."""
    commands_to_place = list(bot.tree.get_commands())
    bot.tree.clear_commands(guild=None)

    for command in commands_to_place:
        cog = command.binding
        scope = getattr(cog, "guild_scope", "main")
        target_id = recruitment_id if scope == RECRUITMENT_SCOPE else main_id
        bot.tree.add_command(command, guild=discord.Object(id=target_id))


@bot.check
async def prefix_commands_are_main_only(ctx: commands.Context) -> bool:
    """Legacy `!` commands never run in the recruitment server or in DMs."""
    main_id = guild_id("MAIN_GUILD_ID")
    return ctx.guild is not None and main_id is not None and ctx.guild.id == main_id


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    """Keep wrong-server prefix commands quiet; surface other command errors."""
    if isinstance(error, commands.CheckFailure):
        return
    raise error


@bot.event
async def on_ready():
    connected = ", ".join(guild.name for guild in bot.guilds)
    print(f"Qwerty is ready as {bot.user}. Connected to: {connected}")


async def sync_guild_commands(main_id: int, recruitment_id: int) -> None:
    """Delete stale globals, then publish each server's private command set."""
    await bot.tree.sync()  # Empty global registry removes previously global commands.
    main_commands = await bot.tree.sync(guild=discord.Object(id=main_id))
    recruitment_commands = await bot.tree.sync(
        guild=discord.Object(id=recruitment_id)
    )
    print(
        f"Synced {len(main_commands)} main-server commands and "
        f"{len(recruitment_commands)} recruitment commands."
    )


async def main():
    token, main_id, recruitment_id = validate_configuration()

    async with bot:
        for extension in (*MAIN_COGS, *RECRUITMENT_COGS):
            await bot.load_extension(extension)
        arrange_slash_commands(main_id, recruitment_id)
        # Discord assigns the application's ID during login. Slash-command
        # syncing requires that ID, so authenticate before syncing and opening
        # the persistent gateway connection.
        await bot.login(token)
        await sync_guild_commands(main_id, recruitment_id)
        await bot.connect(reconnect=True)


if __name__ == "__main__":
    asyncio.run(main())
