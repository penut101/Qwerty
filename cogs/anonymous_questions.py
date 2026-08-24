"""Anonymous question submissions for potential new members."""

from __future__ import annotations

import secrets

import discord
from discord import app_commands
from discord.ext import commands

from cogs.recruitment_common import RECRUITMENT_SCOPE, setting


class AnonymousQuestions(commands.Cog):
    guild_scope = RECRUITMENT_SCOPE

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="ask-anonymously",
        description="Send an anonymous question to the recruitment team",
    )
    @app_commands.describe(question="Your question (your identity will not be forwarded)")
    async def ask_anonymously(
        self, interaction: discord.Interaction, question: str
    ):
        question = question.strip()
        if not question or len(question) > 1500:
            await interaction.response.send_message(
                "Your question must be between 1 and 1,500 characters.", ephemeral=True
            )
            return

        channel_id = setting("ANONYMOUS_QUESTIONS_CHANNEL_ID")
        if not channel_id or not channel_id.isdigit():
            await interaction.response.send_message(
                "Anonymous questions have not been configured yet. Please tell a recruitment leader.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        try:
            channel = self.bot.get_channel(int(channel_id)) or await self.bot.fetch_channel(
                int(channel_id)
            )
            if not isinstance(channel, (discord.TextChannel, discord.Thread)):
                raise TypeError("Configured destination is not a text channel")
            submission_id = secrets.token_hex(3).upper()
            embed = discord.Embed(
                title="Anonymous PNM Question",
                description=question,
                color=discord.Color.from_rgb(0, 107, 143),
            )
            embed.set_footer(text=f"Submission {submission_id}")
            await channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
        except (discord.DiscordException, TypeError):
            await interaction.followup.send(
                "I couldn't deliver that question. Please tell a recruitment leader that the destination channel needs attention.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            f"Your anonymous question was sent. Reference: `{submission_id}`",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(AnonymousQuestions(bot))
