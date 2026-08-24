"""Shared configuration and access checks for recruitment-only cogs.

Keeping guild IDs and role names here prevents each feature from developing its
own slightly different idea of who is allowed to do what.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

import discord


# The marker is read by bot.py when it places slash commands into a guild.
RECRUITMENT_SCOPE = "recruitment"


def _server_config() -> dict[str, str]:
    """Load non-token server settings from the ignored local config file."""
    config_path = Path(os.getenv("QWERTY_SERVER_CONFIG", "server_config.json"))
    try:
        with config_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def setting(name: str, default: str = "") -> str:
    """Read an environment override, then local config, then a default."""
    environment_value = os.getenv(name)
    if environment_value is not None and environment_value.strip():
        return environment_value.strip()
    value = _server_config().get(name, default)
    return str(value).strip()


def data_dir() -> Path:
    """Return the directory used for runtime JSON records."""
    return Path(os.getenv("QWERTY_DATA_DIR", "data"))


def timezone() -> ZoneInfo:
    """Return the timezone used for event and attendance timestamps."""
    return ZoneInfo(os.getenv("QWERTY_TIMEZONE", "America/New_York"))


def guild_id(environment_name: str) -> int | None:
    """Read a Discord guild ID, returning None while setup is incomplete."""
    value = setting(environment_name)
    return int(value) if value.isdigit() else None


def is_guild_member(user_id: int, bot: discord.Client, environment_name: str) -> bool:
    """Check a configured server's member cache for a Discord user."""
    configured_id = guild_id(environment_name)
    guild = bot.get_guild(configured_id) if configured_id else None
    return bool(guild and guild.get_member(user_id))


def is_recruitment_member(user_id: int, bot: discord.Client) -> bool:
    """Check whether a user belongs to the recruitment server."""
    return is_guild_member(user_id, bot, "RECRUITMENT_GUILD_ID")


def is_main_member(user_id: int, bot: discord.Client) -> bool:
    """Check whether a user belongs to the main server."""
    return is_guild_member(user_id, bot, "MAIN_GUILD_ID")


async def require_recruitment_staff(interaction: discord.Interaction) -> bool:
    """Allow Manage Server users or members with the configured staff role."""
    recruitment_id = guild_id("RECRUITMENT_GUILD_ID")
    correct_guild = recruitment_id is not None and interaction.guild_id == recruitment_id
    if correct_guild and isinstance(interaction.user, discord.Member):
        staff_role = setting("RECRUITMENT_ADMIN_ROLE", "Recruitment Team")
        is_staff = interaction.user.guild_permissions.manage_guild or any(
            role.name == staff_role for role in interaction.user.roles
        )
        if is_staff:
            return True

    message = "You need the configured recruitment staff role to use this command."
    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)
    return False
