"""Codeword-based attendance tracking for the recruitment server."""

from __future__ import annotations

import csv
import io
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
    timezone,
)
from cogs.storage import load_json, save_json


DATA_DIR = data_dir()
CODES_FILE = DATA_DIR / "attendance_codes.json"
RECORDS_FILE = DATA_DIR / "attendance_records.json"
TIMEZONE = timezone()
EVENT_QUESTIONS = {
    "pnm attendance": "How has your first week been?",
}


class RecruitmentAttendance(commands.Cog):
    guild_scope = RECRUITMENT_SCOPE

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.awaiting_response: dict[int, dict[str, str]] = {}

    def _codes(self) -> dict[str, dict[str, str]]:
        return load_json(CODES_FILE, {})

    def _records(self) -> list[dict[str, str]]:
        return load_json(RECORDS_FILE, [])

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Treat a direct message as an attendance codeword."""
        if message.author.bot or not isinstance(message.channel, discord.DMChannel):
            return

        # Only members of the recruitment server may submit recruitment codes.
        if not is_recruitment_member(message.author.id, self.bot):
            return

        submitted_code = message.content.strip().casefold()

        pending = self.awaiting_response.pop(message.author.id, None)
        if pending is not None:
            records = self._records()
            records.append(
                {
                    **pending,
                    "answer": message.content.strip(),
                }
            )
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
        question = EVENT_QUESTIONS.get(match["event_name"].casefold())
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
