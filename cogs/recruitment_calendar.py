"""A lightweight recruitment calendar managed from Discord."""

from __future__ import annotations

import secrets
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from cogs.recruitment_common import (
    RECRUITMENT_SCOPE,
    data_dir,
    require_recruitment_staff,
    timezone,
)
from cogs.storage import load_json, save_json


DATA_DIR = data_dir()
EVENTS_FILE = DATA_DIR / "recruitment_events.json"
TIMEZONE = timezone()


class RecruitmentCalendar(commands.Cog):
    guild_scope = RECRUITMENT_SCOPE

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _events(self) -> list[dict[str, str]]:
        return load_json(EVENTS_FILE, [])

    @app_commands.command(name="calendar", description="View upcoming recruitment events")
    async def calendar(self, interaction: discord.Interaction):
        now = datetime.now(TIMEZONE)
        upcoming = sorted(
            (
                event
                for event in self._events()
                if datetime.fromisoformat(event["starts_at"]) >= now
            ),
            key=lambda event: event["starts_at"],
        )[:10]
        if not upcoming:
            await interaction.response.send_message(
                "There are no upcoming recruitment events yet."
            )
            return

        embed = discord.Embed(
            title="Recruitment Calendar",
            color=discord.Color.from_rgb(0, 107, 143),
        )
        for event in upcoming:
            starts_at = datetime.fromisoformat(event["starts_at"])
            unix_time = int(starts_at.timestamp())
            details = [f"<t:{unix_time}:F> · <t:{unix_time}:R>"]
            if event.get("location"):
                details.append(f"📍 {event['location']}")
            if event.get("details"):
                details.append(event["details"])
            embed.add_field(
                name=event["name"], value="\n".join(details), inline=False
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="calendar-add", description="Add a recruitment event")
    @app_commands.describe(
        name="Event name",
        date="Date in YYYY-MM-DD format",
        time="Time in 24-hour HH:MM format",
        location="Optional location",
        details="Optional short description",
    )
    async def add_event(
        self,
        interaction: discord.Interaction,
        name: str,
        date: str,
        time: str,
        location: str | None = None,
        details: str | None = None,
    ):
        if not await require_recruitment_staff(interaction):
            return
        try:
            starts_at = datetime.strptime(
                f"{date.strip()} {time.strip()}", "%Y-%m-%d %H:%M"
            ).replace(tzinfo=TIMEZONE)
        except ValueError:
            await interaction.response.send_message(
                "Use `YYYY-MM-DD` for the date and 24-hour `HH:MM` for the time.",
                ephemeral=True,
            )
            return
        if starts_at < datetime.now(TIMEZONE):
            await interaction.response.send_message(
                "The event must be scheduled in the future.", ephemeral=True
            )
            return
        if not name.strip() or len(name.strip()) > 100:
            await interaction.response.send_message(
                "Provide an event name no longer than 100 characters.", ephemeral=True
            )
            return
        if len((location or "").strip()) > 200 or len((details or "").strip()) > 700:
            await interaction.response.send_message(
                "Locations may be 200 characters and details may be 700 characters.",
                ephemeral=True,
            )
            return

        events = self._events()
        event = {
            "id": secrets.token_hex(3),
            "name": name.strip(),
            "starts_at": starts_at.isoformat(timespec="minutes"),
            "location": (location or "").strip(),
            "details": (details or "").strip(),
        }
        events.append(event)
        save_json(EVENTS_FILE, events)
        await interaction.response.send_message(
            f"Added **{event['name']}** to the calendar with ID `{event['id']}`.",
            ephemeral=True,
        )

    @app_commands.command(name="calendar-remove", description="Remove a recruitment event")
    @app_commands.describe(event_id="Event ID returned by /calendar-manage")
    async def remove_event(self, interaction: discord.Interaction, event_id: str):
        if not await require_recruitment_staff(interaction):
            return
        events = self._events()
        remaining = [event for event in events if event["id"] != event_id.strip()]
        if len(remaining) == len(events):
            await interaction.response.send_message(
                "No event has that ID. Use `/calendar-manage` to view IDs.",
                ephemeral=True,
            )
            return
        removed = next(event for event in events if event["id"] == event_id.strip())
        save_json(EVENTS_FILE, remaining)
        await interaction.response.send_message(
            f"Removed **{removed['name']}** from the calendar.", ephemeral=True
        )

    @app_commands.command(
        name="calendar-manage", description="View recruitment event IDs"
    )
    async def manage_calendar(self, interaction: discord.Interaction):
        if not await require_recruitment_staff(interaction):
            return
        events = sorted(self._events(), key=lambda event: event["starts_at"])
        if not events:
            await interaction.response.send_message(
                "The recruitment calendar is empty.", ephemeral=True
            )
            return
        lines = [
            f"`{event['id']}` — **{event['name']}** — {datetime.fromisoformat(event['starts_at']).strftime('%b %d, %Y at %I:%M %p')}"
            for event in events
        ]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(RecruitmentCalendar(bot))
