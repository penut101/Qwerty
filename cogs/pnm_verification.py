"""Automatic information collection for members who receive the PNM role."""

from __future__ import annotations

import asyncio
import csv
import io
import logging
import re
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


ONBOARDING_FILE = data_dir() / "pnm_onboarding.json"
TIMEZONE = timezone()
PITT_EMAIL_PATTERN = re.compile(r"[A-Z0-9._%+-]+@pitt\.edu", re.IGNORECASE)
LOGGER = logging.getLogger(__name__)


def _pnm_role(guild: discord.Guild) -> discord.Role | None:
    role_name = setting("PNM_ONBOARDING_ROLE", "PNM")
    return discord.utils.get(guild.roles, name=role_name)


def _has_pnm_role(member: discord.Member) -> bool:
    role = _pnm_role(member.guild)
    return role is not None and role in member.roles


class OnboardingModal(discord.ui.Modal, title="PNM Information"):
    first_name = discord.ui.TextInput(label="First name", placeholder="Your first name", max_length=50)
    last_name = discord.ui.TextInput(label="Last name", placeholder="Your last name", max_length=50)
    phone_number = discord.ui.TextInput(label="Phone number", placeholder="412-555-0123", max_length=25)
    pitt_email = discord.ui.TextInput(label="Pitt email", placeholder="abc123@pitt.edu", max_length=100)
    discord_username = discord.ui.TextInput(label="Discord username", placeholder="Your current Discord username", max_length=50)

    def __init__(self, cog: "PNMOnboarding", username: str):
        super().__init__()
        self.cog = cog
        self.discord_username.default = username

    async def on_submit(self, interaction: discord.Interaction):
        await self.cog.submit_onboarding(
            interaction,
            first_name=str(self.first_name),
            last_name=str(self.last_name),
            phone_number=str(self.phone_number),
            pitt_email=str(self.pitt_email),
            discord_username=str(self.discord_username),
        )


class OnboardingStartView(discord.ui.View):
    def __init__(self, cog: "PNMOnboarding"):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(
        label="Complete PNM Form",
        style=discord.ButtonStyle.primary,
        custom_id="pnm_onboarding:start",
    )
    async def start_onboarding(self, interaction: discord.Interaction, _: discord.ui.Button):
        recruitment_id = guild_id("RECRUITMENT_GUILD_ID")
        guild = self.cog.bot.get_guild(recruitment_id) if recruitment_id else None
        member = guild.get_member(interaction.user.id) if guild else None
        if member is None or not _has_pnm_role(member):
            await interaction.response.send_message(
                "You must have the PNM role in the recruitment server to use this form."
            )
            return
        if self.cog.is_complete(member.id):
            await interaction.response.send_message("Your PNM information has already been submitted.")
            return
        await interaction.response.send_modal(OnboardingModal(self.cog, interaction.user.name))


class PNMOnboarding(commands.Cog):
    """Ask PNMs for required contact information and report it automatically."""

    guild_scope = RECRUITMENT_SCOPE

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._prompt_lock = asyncio.Lock()

    def _records(self) -> dict[str, dict[str, str]]:
        return load_json(ONBOARDING_FILE, {})

    def is_complete(self, member_id: int) -> bool:
        return self._records().get(str(member_id), {}).get("status") == "completed"

    def _join_log_channel_id(self) -> int | None:
        value = setting("PNM_JOIN_LOG_CHANNEL_ID")
        return int(value) if value.isdigit() else None

    async def cog_load(self):
        self.bot.add_view(OnboardingStartView(self))

    async def _send_onboarding_prompt(
        self, member: discord.Member, *, force: bool = False
    ) -> tuple[bool, str]:
        if not _has_pnm_role(member):
            return False, "member does not have the PNM role"

        records = self._records()
        existing_status = records.get(str(member.id), {}).get("status")
        if existing_status == "completed":
            return False, "member already completed the form"
        if existing_status == "prompted" and not force:
            return False, "form already sent"

        try:
            await member.send(
                embed=discord.Embed(
                    title="Kappa Theta Pi PNM Information",
                    description=(
                        "Please complete this required form. Qwerty will send your first and "
                        "last name, phone number, Pitt email, and Discord username to the "
                        "private PNM join log. Qwerty does not save those answers in its local "
                        "data files."
                    ),
                    color=discord.Color.from_rgb(0, 107, 143),
                ),
                view=OnboardingStartView(self),
            )
        except discord.Forbidden:
            return False, "direct messages are closed"
        except discord.DiscordException:
            return False, "Discord could not deliver the message"

        records[str(member.id)] = {
            "status": "prompted",
            "prompted_at": datetime.now(TIMEZONE).isoformat(timespec="seconds"),
            "completed_at": "",
        }
        save_json(ONBOARDING_FILE, records)
        return True, "PNM form sent"

    async def _notify_prompt_failure(self, member: discord.Member, detail: str) -> None:
        channel_id = self._join_log_channel_id()
        if channel_id is None:
            return
        try:
            channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(
                channel_id
            )
            if not isinstance(channel, (discord.TextChannel, discord.Thread)):
                return
            await channel.send(
                embed=discord.Embed(
                    title="PNM Form DM Failed",
                    description=(
                        f"I could not send the PNM form to {member.mention} (`{member.id}`): "
                        f"**{detail}**. Ask them to enable server DMs, then use `/pnm-form-send`."
                    ),
                    color=discord.Color.orange(),
                ),
                allowed_mentions=discord.AllowedMentions.none(),
            )
        except discord.DiscordException:
            pass

    async def _prompt_if_eligible(self, member: discord.Member) -> None:
        async with self._prompt_lock:
            if member.bot or member.guild.id != guild_id("RECRUITMENT_GUILD_ID"):
                return
            if not _has_pnm_role(member):
                return
            sent, detail = await self._send_onboarding_prompt(member)
            if not sent and detail not in {"form already sent", "member already completed the form"}:
                await self._notify_prompt_failure(member, detail)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self._prompt_if_eligible(member)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Catch invite-assigned PNM roles that arrive just after the join event."""
        role = _pnm_role(after.guild)
        if role is None or role in before.roles or role not in after.roles:
            return
        await self._prompt_if_eligible(after)

    async def submit_onboarding(
        self,
        interaction: discord.Interaction,
        *,
        first_name: str,
        last_name: str,
        phone_number: str,
        pitt_email: str,
        discord_username: str,
    ):
        first_name = first_name.strip()
        last_name = last_name.strip()
        pitt_email = pitt_email.strip().lower()
        submitted_username = discord_username.strip().removeprefix("@").casefold()
        digits = re.sub(r"\D", "", phone_number)
        if len(digits) == 11 and digits.startswith("1"):
            digits = digits[1:]

        errors = []
        if not first_name or not last_name:
            errors.append("Enter both your first and last name.")
        if len(digits) != 10:
            errors.append("Enter a valid 10-digit US phone number.")
        if PITT_EMAIL_PATTERN.fullmatch(pitt_email) is None:
            errors.append("Use your `@pitt.edu` email address.")
        if submitted_username != interaction.user.name.casefold():
            errors.append(f"Your Discord username must match `{interaction.user.name}`.")
        if errors:
            await interaction.response.send_message("\n".join(errors))
            return

        recruitment_id = guild_id("RECRUITMENT_GUILD_ID")
        guild = self.bot.get_guild(recruitment_id) if recruitment_id else None
        member = guild.get_member(interaction.user.id) if guild else None
        if member is None or not _has_pnm_role(member):
            await interaction.response.send_message(
                "You must still have the PNM role in the recruitment server."
            )
            return
        if self.is_complete(member.id):
            await interaction.response.send_message("Your PNM information has already been submitted.")
            return

        channel_id = self._join_log_channel_id()
        if channel_id is None:
            await interaction.response.send_message(
                "The PNM join log is not configured yet. Please contact the Recruitment Team."
            )
            return

        await interaction.response.defer()
        formatted_phone = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        embed = discord.Embed(
            title="PNM Join Report",
            description=f"Form completed by {member.mention} (`{member.id}`)",
            color=discord.Color.green(),
            timestamp=datetime.now(TIMEZONE),
        )
        embed.add_field(name="First name", value=first_name, inline=True)
        embed.add_field(name="Last name", value=last_name, inline=True)
        embed.add_field(name="Phone number", value=formatted_phone, inline=False)
        embed.add_field(name="Pitt email", value=pitt_email, inline=False)
        embed.add_field(name="Discord username", value=f"@{interaction.user.name}", inline=False)
        embed.set_footer(text="PNM form completed")

        try:
            channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
            if not isinstance(channel, (discord.TextChannel, discord.Thread)):
                raise TypeError("PNM join log is not a text channel")
            if channel.guild.id != member.guild.id:
                raise TypeError("PNM join log is outside the recruitment server")
            report = await channel.send(
                embed=embed,
                allowed_mentions=discord.AllowedMentions.none(),
            )
        except (discord.DiscordException, TypeError):
            LOGGER.exception(
                "Could not deliver PNM form for member %s to join-log channel %s",
                member.id,
                channel_id,
            )
            await interaction.followup.send(
                "I couldn't deliver your form. Please contact the Recruitment Team."
            )
            return

        records = self._records()
        records[str(member.id)] = {
            "status": "completed",
            "prompted_at": records.get(str(member.id), {}).get("prompted_at", ""),
            "completed_at": datetime.now(TIMEZONE).isoformat(timespec="seconds"),
            "report_message_id": str(report.id),
        }
        save_json(ONBOARDING_FILE, records)
        await interaction.followup.send("Thanks! Your PNM information has been submitted successfully.")

    @app_commands.command(
        name="pnm-form-send",
        description="Send or resend the required PNM form to one member",
    )
    async def send_onboarding_form(
        self, interaction: discord.Interaction, member: discord.Member
    ):
        if not await require_recruitment_staff(interaction):
            return
        await interaction.response.defer(ephemeral=True)
        sent, detail = await self._send_onboarding_prompt(member, force=True)
        prefix = "Sent" if sent else "Did not send"
        await interaction.followup.send(
            f"{prefix} the PNM form to **{member.display_name}**: {detail}.",
            ephemeral=True,
        )

    @app_commands.command(
        name="pnm-form-send-all",
        description="Resend the required form to every PNM who has not completed it",
    )
    async def send_all_onboarding_forms(self, interaction: discord.Interaction):
        if not await require_recruitment_staff(interaction):
            return

        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        role = _pnm_role(guild) if guild is not None else None
        if role is None:
            role_name = setting("PNM_ONBOARDING_ROLE", "PNM")
            await interaction.followup.send(
                f"Could not find the configured PNM role: **{role_name}**.",
                ephemeral=True,
            )
            return

        pnms = [member for member in role.members if not member.bot]
        sent_count = 0
        completed_count = 0
        failure_counts: dict[str, int] = {}

        async with self._prompt_lock:
            for member in pnms:
                sent, detail = await self._send_onboarding_prompt(member, force=True)
                if sent:
                    sent_count += 1
                elif detail == "member already completed the form":
                    completed_count += 1
                else:
                    failure_counts[detail] = failure_counts.get(detail, 0) + 1

        failed_count = sum(failure_counts.values())
        summary = [
            f"Processed **{len(pnms)}** PNM(s).",
            f"Sent: **{sent_count}**",
            f"Skipped (already completed): **{completed_count}**",
            f"Failed: **{failed_count}**",
        ]
        if failure_counts:
            summary.append(
                "Failure reasons: "
                + ", ".join(
                    f"{detail} ({count})" for detail, count in sorted(failure_counts.items())
                )
            )
        await interaction.followup.send("\n".join(summary), ephemeral=True)

    @app_commands.command(
        name="pnm-information-export",
        description="Download all submitted PNM information as a CSV sheet",
    )
    async def export_pnm_information(self, interaction: discord.Interaction):
        if not await require_recruitment_staff(interaction):
            return

        await interaction.response.defer(ephemeral=True)
        channel_id = self._join_log_channel_id()
        if channel_id is None:
            await interaction.followup.send(
                "The PNM join log is not configured yet.", ephemeral=True
            )
            return

        try:
            channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
            if not isinstance(channel, (discord.TextChannel, discord.Thread)):
                raise TypeError("PNM join log is not a text channel")

            rows = []
            for member_id, record in self._records().items():
                message_id = record.get("report_message_id", "")
                if record.get("status") != "completed" or not message_id.isdigit():
                    continue
                try:
                    report = await channel.fetch_message(int(message_id))
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    LOGGER.warning("Could not fetch PNM report message %s", message_id)
                    continue
                if not report.embeds:
                    continue
                fields = {
                    field.name.casefold(): field.value
                    for field in report.embeds[0].fields
                }
                rows.append(
                    {
                        "discord_user_id": member_id,
                        "first_name": fields.get("first name", ""),
                        "last_name": fields.get("last name", ""),
                        "phone_number": fields.get("phone number", ""),
                        "pitt_email": fields.get("pitt email", ""),
                        "discord_username": fields.get("discord username", ""),
                        "completed_at": record.get("completed_at", ""),
                    }
                )
        except (discord.DiscordException, TypeError):
            LOGGER.exception("Could not read PNM join log channel %s", channel_id)
            await interaction.followup.send(
                "I couldn't read the PNM join log.", ephemeral=True
            )
            return

        if not rows:
            await interaction.followup.send(
                "No completed PNM information could be found.", ephemeral=True
            )
            return

        columns = [
            "discord_user_id",
            "first_name",
            "last_name",
            "phone_number",
            "pitt_email",
            "discord_username",
            "completed_at",
        ]
        output = io.StringIO(newline="")
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
        payload = io.BytesIO(output.getvalue().encode("utf-8-sig"))
        await interaction.followup.send(
            file=discord.File(payload, filename="qwerty_pnm_information.csv"),
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(PNMOnboarding(bot))
