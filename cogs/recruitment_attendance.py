"""Codeword-based attendance tracking for the recruitment server."""

from __future__ import annotations

import csv
import io
import logging
import secrets
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from cogs.recruitment_common import (
    RECRUITMENT_SCOPE,
    data_dir,
    is_main_member,
    is_recruitment_member,
    require_recruitment_staff,
    setting,
    timezone,
)
from cogs.storage import load_json, save_json


DATA_DIR = data_dir()
CODES_FILE = DATA_DIR / "attendance_codes.json"
RECORDS_FILE = DATA_DIR / "attendance_records.json"
TIMEZONE = timezone()
LOGGER = logging.getLogger(__name__)
EVENT_QUESTIONS_BY_CODE = {
    "infosesh": "How has your first week been?",
}
DEFAULT_ATTENDANCE_LOG_CHANNEL_ID = "1536778474755334235"


class RecruitmentAttendance(commands.Cog):
    guild_scope = RECRUITMENT_SCOPE

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.awaiting_response: dict[int, dict[str, str]] = {}

    def _codes(self) -> dict[str, dict[str, str]]:
        return load_json(CODES_FILE, {})

    def _records(self) -> list[dict[str, str]]:
        return load_json(RECORDS_FILE, [])

    def _attendance_log_channel_id(self) -> int | None:
        value = setting(
            "PNM_ATTENDANCE_LOG_CHANNEL_ID", DEFAULT_ATTENDANCE_LOG_CHANNEL_ID
        )
        return int(value) if value.isdigit() else None

    async def _post_attendance_report(
        self, record: dict[str, str]
    ) -> discord.Message:
        channel_id = self._attendance_log_channel_id()
        if channel_id is None:
            raise TypeError("PNM attendance log channel is not configured")

        channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(
            channel_id
        )
        if not isinstance(channel, (discord.TextChannel, discord.Thread)):
            raise TypeError("PNM attendance log is not a text channel")

        embed = discord.Embed(
            title="PNM Attendance Report",
            description=(
                f"**Question**\n{record['question']}\n\n"
                f"**Answer**\n{record['answer']}"
            ),
            color=discord.Color.green(),
            timestamp=datetime.fromisoformat(record["checked_in_at"]),
        )
        embed.add_field(name="Event", value=record["event_name"], inline=False)
        embed.add_field(name="Display name", value=record["display_name"], inline=True)
        embed.add_field(name="Discord username", value=record["discord_name"], inline=True)
        embed.add_field(name="Discord user ID", value=record["discord_user_id"], inline=False)
        return await channel.send(
            embed=embed,
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Treat a direct message as an attendance codeword."""
        if message.author.bot or not isinstance(message.channel, discord.DMChannel):
            return

        # Only members of the recruitment server may submit recruitment codes.
        if not is_recruitment_member(message.author.id, self.bot):
            return

        submitted_code = message.content.strip().casefold()

        pending = self.awaiting_response.get(message.author.id)
        if pending is not None:
            record = {
                **pending,
                "answer": message.content.strip(),
            }
            try:
                report = await self._post_attendance_report(record)
            except (discord.DiscordException, TypeError, ValueError):
                LOGGER.exception(
                    "Could not post attendance report for member %s",
                    message.author.id,
                )
                await message.channel.send(
                    "I couldn't post your attendance report. Your answer is still pending; "
                    "please contact the Recruitment Team."
                )
                return

            self.awaiting_response.pop(message.author.id, None)
            record["report_message_id"] = str(report.id)
            records = self._records()
            records.append(record)
            save_json(RECORDS_FILE, records)
            await message.channel.send("Thanks! Your response has been recorded.")
            return

        match = next(
            (
                entry
                for entry in self._codes().values()
                if entry["code"].casefold() == submitted_code
            ),
            None,
        )
        if match is None:
            # Main-server attendance may be waiting for this dual member's answer.
            if is_main_member(message.author.id, self.bot):
                return
            await message.channel.send(
                "That is not an active attendance codeword. Check the spelling and try again."
            )
            return

        records = self._records()
        already_checked_in = any(
            record["event_id"] == match["id"]
            and record["discord_user_id"] == str(message.author.id)
            for record in records
        )
        if already_checked_in:
            await message.channel.send(
                f"You are already checked in for **{match['event_name']}**."
            )
            return

        record = {
            "event_id": match["id"],
            "event_name": match["event_name"],
            "discord_user_id": str(message.author.id),
            "discord_name": str(message.author),
            "display_name": message.author.display_name,
            "checked_in_at": datetime.now(TIMEZONE).isoformat(timespec="seconds"),
        }
        question = EVENT_QUESTIONS_BY_CODE.get(match["code"].casefold())
        if question:
            record["question"] = question
            self.awaiting_response[message.author.id] = record
            await message.channel.send(
                f"You're checked in for **{match['event_name']}**.\n\n"
                f"Quick question:\n**{question}**"
            )
            return

        record.update({"question": "", "answer": ""})
        records.append(record)
        save_json(RECORDS_FILE, records)
        await message.channel.send(
            f"You're checked in for **{match['event_name']}**. Thank you!"
        )

    @app_commands.command(
        name="attendance-code-add",
        description="Create or replace an event attendance codeword",
    )
    @app_commands.describe(event="Event name", codeword="Codeword PNMs will DM to Qwerty")
    async def add_code(
        self, interaction: discord.Interaction, event: str, codeword: str
    ):
        if not await require_recruitment_staff(interaction):
            return
        event = event.strip()
        codeword = codeword.strip()
        if (
            not event
            or not codeword
            or len(event) > 100
            or len(codeword) > 100
            or any(character.isspace() for character in codeword)
        ):
            await interaction.response.send_message(
                "Provide an event name and a single-word codeword (100 characters maximum).",
                ephemeral=True,
            )
            return

        codes = self._codes()
        duplicate = next(
            (
                entry
                for key, entry in codes.items()
                if key != event.casefold() and entry["code"].casefold() == codeword.casefold()
            ),
            None,
        )
        if duplicate:
            await interaction.response.send_message(
                f"That codeword is already assigned to **{duplicate['event_name']}**.",
                ephemeral=True,
            )
            return

        key = event.casefold()
        existing = codes.get(key)
        codes[key] = {
            "id": existing["id"] if existing else secrets.token_hex(4),
            "event_name": event,
            "code": codeword,
        }
        save_json(CODES_FILE, codes)
        await interaction.response.send_message(
            f"Attendance is open for **{event}**. Codeword: `{codeword}`",
            ephemeral=True,
        )

    @app_commands.command(
        name="attendance-code-remove", description="Close attendance for an event"
    )
    @app_commands.describe(event="Event name shown by /attendance-code-list")
    async def remove_code(self, interaction: discord.Interaction, event: str):
        if not await require_recruitment_staff(interaction):
            return
        codes = self._codes()
        removed = codes.pop(event.strip().casefold(), None)
        if removed is None:
            await interaction.response.send_message(
                "No active attendance event has that name.", ephemeral=True
            )
            return
        save_json(CODES_FILE, codes)
        await interaction.response.send_message(
            f"Attendance closed for **{removed['event_name']}**.", ephemeral=True
        )

    @app_commands.command(
        name="attendance-code-list", description="View active attendance codewords"
    )
    async def list_codes(self, interaction: discord.Interaction):
        if not await require_recruitment_staff(interaction):
            return
        codes = self._codes().values()
        if not codes:
            await interaction.response.send_message(
                "There are no active attendance codewords.", ephemeral=True
            )
            return
        lines = [f"• **{entry['event_name']}** — `{entry['code']}`" for entry in codes]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    @app_commands.command(
        name="attendance-export", description="Download all attendance records as CSV"
    )
    async def export_attendance(self, interaction: discord.Interaction):
        if not await require_recruitment_staff(interaction):
            return
        records = self._records()
        if not records:
            await interaction.response.send_message(
                "No attendance has been recorded yet.", ephemeral=True
            )
            return

        output = io.StringIO(newline="")
        columns = [
            "event_id",
            "event_name",
            "discord_user_id",
            "discord_name",
            "display_name",
            "checked_in_at",
            "question",
            "answer",
        ]
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(
            {column: record.get(column, "") for column in columns}
            for record in records
        )
        payload = io.BytesIO(output.getvalue().encode("utf-8"))
        await interaction.response.send_message(
            file=discord.File(payload, filename="qwerty_attendance.csv"), ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(RecruitmentAttendance(bot))
