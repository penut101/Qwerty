"""Consent-based movement from the recruitment server to the main server.

Discord does not permit bots to move users between servers. This cog sends the
main-server invite to eligible members, records delivery, and completes the
transition only after each person chooses to join.
"""

from __future__ import annotations

import asyncio
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from cogs.recruitment_common import (
    RECRUITMENT_SCOPE,
    data_dir,
    guild_id,
    require_recruitment_staff,
    setting,
    timezone,
)
from cogs.storage import load_json, save_json


TRANSITIONS_FILE = data_dir() / "member_transitions.json"
TIMEZONE = timezone()


class MemberTransition(commands.Cog):
    """Invite PNMs to the main server and track successful joins."""

    guild_scope = RECRUITMENT_SCOPE

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _transitions(self) -> dict[str, dict[str, str]]:
        return load_json(TRANSITIONS_FILE, {})

    def _main_invite(self) -> str | None:
        invite = setting("MAIN_SERVER_INVITE_URL")
        return invite or None

    def _main_guild(self) -> discord.Guild | None:
        main_id = guild_id("MAIN_GUILD_ID")
        return self.bot.get_guild(main_id) if main_id else None

    async def _send_invite(self, member: discord.Member) -> tuple[bool, str]:
        """Send one invite and persist its delivery status."""
        invite = self._main_invite()
        if invite is None:
            return False, "MAIN_SERVER_INVITE_URL is not configured"

        main_guild = self._main_guild()
        if main_guild and main_guild.get_member(member.id):
            return False, "already in the main server"

        try:
            await member.send(
                "Congratulations! You are invited to join the Kappa Theta Pi main "
                f"Discord server. Join when you're ready:\n{invite}"
            )
        except discord.Forbidden:
            status = "dm_blocked"
            detail = "direct messages are closed"
        except discord.DiscordException:
            status = "delivery_failed"
            detail = "Discord could not deliver the message"
        else:
            status = "invited"
            detail = "invite sent"

        transitions = self._transitions()
        transitions[str(member.id)] = {
            "discord_name": str(member),
            "display_name": member.display_name,
            "status": status,
            "invited_at": datetime.now(TIMEZONE).isoformat(timespec="seconds"),
            "joined_at": transitions.get(str(member.id), {}).get("joined_at", ""),
        }
        save_json(TRANSITIONS_FILE, transitions)
        return status == "invited", detail

    @app_commands.command(
        name="transition-invite", description="Invite one recruitment member to the main server"
    )
    @app_commands.describe(member="Recruitment member who should receive the invite")
    async def invite_member(
        self, interaction: discord.Interaction, member: discord.Member
    ):
        if not await require_recruitment_staff(interaction):
            return
        await interaction.response.defer(ephemeral=True)
        sent, detail = await self._send_invite(member)
        prefix = "Sent" if sent else "Did not send"
        await interaction.followup.send(
            f"{prefix} the main-server invite to **{member.display_name}**: {detail}.",
            ephemeral=True,
        )

    @app_commands.command(
        name="transition-invite-all",
        description="Invite all eligible PNMs to the main server",
    )
    @app_commands.describe(
        confirm="Must be true to send direct messages",
    )
    async def invite_all(self, interaction: discord.Interaction, confirm: bool):
        if not await require_recruitment_staff(interaction):
            return
        if not confirm:
            await interaction.response.send_message(
                "Nothing was sent. Run the command with `confirm: True` when ready.",
                ephemeral=True,
            )
            return
        if self._main_invite() is None:
            await interaction.response.send_message(
                "Set MAIN_SERVER_INVITE_URL before sending invitations.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        recruitment_guild = interaction.guild
        main_guild = self._main_guild()
        source_role_name = setting("TRANSITION_SOURCE_ROLE", "Accepted PNM")

        # Requiring a source role prevents accidental DMs to staff, alumni, or bots.
        eligible = [
            member
            for member in recruitment_guild.members
            if not member.bot
            and any(role.name == source_role_name for role in member.roles)
            and not (main_guild and main_guild.get_member(member.id))
        ]

        sent = 0
        failed = 0
        for member in eligible:
            delivered, _ = await self._send_invite(member)
            sent += int(delivered)
            failed += int(not delivered)
            # A small pause keeps the batch polite and lets discord.py handle rate limits.
            await asyncio.sleep(0.75)

        await interaction.followup.send(
            f"Transition invitations complete: **{sent} sent**, **{failed} failed**, "
            f"**{len(eligible)} eligible** via the `{source_role_name}` role.",
            ephemeral=True,
        )

    @app_commands.command(
        name="transition-status", description="View invitation and join totals"
    )
    async def transition_status(self, interaction: discord.Interaction):
        if not await require_recruitment_staff(interaction):
            return
        transitions = self._transitions()
        counts = {"invited": 0, "joined": 0, "dm_blocked": 0, "delivery_failed": 0}
        for record in transitions.values():
            status = record.get("status", "delivery_failed")
            counts[status] = counts.get(status, 0) + 1

        pending = [
            record["display_name"]
            for record in transitions.values()
            if record.get("status") == "invited"
        ]
        pending_preview = ", ".join(pending[:20]) or "None"
        if len(pending) > 20:
            pending_preview += f" and {len(pending) - 20} more"

        await interaction.response.send_message(
            "**Member transition status**\n"
            f"Joined: **{counts['joined']}**\n"
            f"Invited and pending: **{counts['invited']}**\n"
            f"DMs closed: **{counts['dm_blocked']}**\n"
            f"Other delivery failures: **{counts['delivery_failed']}**\n"
            f"Pending members: {pending_preview}",
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Complete a tracked transition when an invited member joins main."""
        if member.guild.id != guild_id("MAIN_GUILD_ID"):
            return

        transitions = self._transitions()
        record = transitions.get(str(member.id))
        if record is None:
            return

        role_name = setting("MAIN_NEW_MEMBER_ROLE", "New Member")
        role = discord.utils.get(member.guild.roles, name=role_name)
        if role:
            try:
                await member.add_roles(role, reason="Completed recruitment transition")
            except discord.DiscordException:
                # Joining is still recorded if role hierarchy prevents assignment.
                pass

        record["status"] = "joined"
        record["joined_at"] = datetime.now(TIMEZONE).isoformat(timespec="seconds")
        record["display_name"] = member.display_name
        save_json(TRANSITIONS_FILE, transitions)


async def setup(bot: commands.Bot):
    await bot.add_cog(MemberTransition(bot))
