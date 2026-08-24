"""Publish and maintain the recruitment server's static information posts."""

from __future__ import annotations

import asyncio
import logging

import discord
from discord import app_commands
from discord.ext import commands

from cogs.recruitment_common import (
    RECRUITMENT_SCOPE,
    data_dir,
    guild_id,
    require_recruitment_staff,
    setting,
)
from cogs.storage import load_json, save_json


LOGGER = logging.getLogger(__name__)
POSTS_FILE = data_dir() / "recruitment_information_posts.json"
EMBED_COLOR = discord.Color.from_rgb(0, 107, 143)

CHANNEL_SETTINGS = {
    "introductions": "RECRUITMENT_INTRODUCTIONS_CHANNEL_ID",
    "rush_schedule": "RECRUITMENT_RUSH_SCHEDULE_CHANNEL_ID",
    "faq": "RECRUITMENT_FAQ_CHANNEL_ID",
}


def _introductions_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Introductions",
        description="## Recruitment Team\nMeet the people helping lead Kappa Theta Pi recruitment.",
        color=EMBED_COLOR,
    )
    embed.add_field(
        name="Jess Wagner",
        value=(
            "**Position:** VP of Membership\n"
            "**Majors:** Computer Science & Data Science\n"
            "**Year:** Senior\n"
            "**Preferred Contact:** Discord DM (@jesswagner) or email (JAW479@pitt.edu)\n"
            "**Fun Fact:** I love Taco Bell\n\u200b"
        ),
        inline=False,
    )
    embed.add_field(
        name="Natalie Goldsworthy",
        value=(
            "**Position:** President\n"
            "**Majors:** Computer Science, Data Science, and Digital Narrative & Interactive Design\n"
            "**Minor/Certificate:** English Literature minor, Digital Studies and Media certificate\n"
            "**Year:** Junior\n"
            "**Preferred Contact:** Discord DM (@_natality), text (724-552-7880), or email (npg26@pitt.edu)\n"
            "**Fun Fact:** I once went to the same Halloween party as Tom Cruise's daughter\n\u200b"
        ),
        inline=False,
    )
    embed.add_field(
        name="Nick Berarducci",
        value=(
            "**Position:** Assistant Recruitment Chair\n"
            "**Major:** Computer Science\n"
            "**Minor:** Information Science\n"
            "**Year:** Sophomore\n"
            "**Preferred Contact:** Text (814-746-0190) or email (ngb52@pitt.edu)\n"
            "**Fun Fact:** I'm him"
        ),
        inline=False,
    )
    return embed


def _rush_schedule_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Rush Schedule",
        description="## Rush Events + Locations 2026",
        color=EMBED_COLOR,
    )
    embed.add_field(
        name="Week 1 (8/31 - 9/4)",
        value=(
            "**Wednesday, 9/2: Information Sessions**\n"
            "**Time:** 7:30-8:00 & 8:00-8:30 PM\n"
            "**Location:** Sennott 5317\n\n"
            "**Thursday, 9/3: Information Sessions**\n"
            "**Time:** 8:00-8:30 & 8:30-9:00 PM\n"
            "**Location:** Sennott 5317\n\u200b"
        ),
        inline=False,
    )
    embed.add_field(
        name="Week 2 (9/7 - 9/11)",
        value=(
            "**Tuesday, 9/8: Cane's Catering Social**\n"
            "**Time:** 6:30-8:00 PM\n"
            "**Location:** Patio behind Posvar; Sennott 5317 if the weather is bad\n\n"
            "**Thursday, 9/10: Game Night**\n"
            "**Time:** 6:15-7:45 PM\n"
            "**Location:** WPU Nordy's Place\n\u200b"
        ),
        inline=False,
    )
    embed.add_field(
        name="Week 3 (9/14 - 9/18)",
        value=(
            "**Monday, 9/14: Speed Friending**\n"
            "**Time:** 9:00-10:00 PM\n"
            "**Location:** 233 David Lawrence Hall\n\n"
            "**Wednesday, 9/16: Resume Review**\n"
            "**Time:** 7:30-8:30 PM\n"
            "**Location:** Sennott 5317\n\n"
            "**Friday, 9/18: Invite-Only Event**\n\u200b"
        ),
        inline=False,
    )
    embed.add_field(
        name="Invite-Only Interviews (9/19 - 9/20)",
        value=(
            "**Saturday, 9/19: Interview Day 1**\n"
            "**Time:** TBD\n"
            "**Location:** 205 David Lawrence\n\n"
            "**Sunday, 9/20: Interview Day 2**\n"
            "**Time:** TBD\n"
            "**Location:** 205 David Lawrence"
        ),
        inline=False,
    )
    return embed


def _faq_embeds() -> tuple[discord.Embed, ...]:
    questions_and_answers = (
        ("What is Kappa Theta Pi?", "A co-ed professional technology fraternity focused on professional development, technical growth, community, and brotherhood."),
        ("Is KTP time-intensive? I'm busy with school/work/other commitments, and I'm worried I'll be too busy.", "KTP is only as time-intensive as you make it. We only require brothers to attend chapter once every other week, with all other events being optional. Although we recommend that brothers take advantage of all our opportunities, you can adjust your participation based on your schedule."),
        ("Do I have to be a certain major to rush?", "Nope! KTP takes students of all majors. However, most of our brothers are in SCI majors."),
        ("Do I have to be a certain year to rush?", "Nope! You can rush as early as your first semester of freshman year."),
        ("What is rush?", "Rush is a series of events where you can learn about KTP, meet brothers, and see if the club is a good fit for you."),
        ("What is a PNM?", "PNM stands for Potential New Member. That's you! It's the title given to individuals rushing KTP who have yet to be inducted into the fraternity."),
        ("Do I have to attend every rush event?", "You don't necessarily have to attend every event, but coming to multiple events gives you more opportunities to meet brothers and learn about KTP. Being active throughout rush also helps us get to know you better when making bid decisions."),
        ("Does rush cost anything?", "Rush events are free to attend."),
        ("What if I'm invited to interview, but none of the available interview times work for me?", "No worries! Just message Jess, Natalie, or Mason, and we'll work with you to find a time that works. We understand it's the same weekend as SteelHacks and that people are busy with work, school, and other obligations."),
        ("When will I know if I got a bid?", "You can expect to hear from us sometime on September 21st or 22nd."),
        ("If I have a question or concern, where should I go?", "If you have any questions or concerns throughout rush, feel free to ask in #general or reach out to a member of the Recruitment Team."),
    )
    return tuple(
        discord.Embed(title=question, description=answer, color=EMBED_COLOR)
        for question, answer in questions_and_answers
    )


def information_embeds() -> dict[str, tuple[discord.Embed, ...]]:
    return {
        "introductions": (_introductions_embed(),),
        "rush_schedule": (_rush_schedule_embed(),),
        "faq": _faq_embeds(),
    }


class RecruitmentInformation(commands.Cog):
    guild_scope = RECRUITMENT_SCOPE

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._sync_lock = asyncio.Lock()

    async def _sync_posts(self) -> dict[str, str]:
        """Create missing posts and edit existing Qwerty-owned posts in place."""
        async with self._sync_lock:
            configured_guild_id = guild_id("RECRUITMENT_GUILD_ID")
            post_state = load_json(POSTS_FILE, {})
            results: dict[str, str] = {}

            for post_name, embeds in information_embeds().items():
                channel_value = setting(CHANNEL_SETTINGS[post_name])
                if not channel_value.isdigit():
                    results[post_name] = "not configured"
                    continue

                channel_id = int(channel_value)
                try:
                    channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
                    if not isinstance(channel, (discord.TextChannel, discord.Thread)):
                        raise TypeError("destination is not a text channel")
                    if configured_guild_id is not None and channel.guild.id != configured_guild_id:
                        raise TypeError("destination is outside the recruitment server")

                    saved_post = post_state.get(post_name, {})
                    saved_message_ids = saved_post.get("message_ids", [])
                    if not isinstance(saved_message_ids, list):
                        saved_message_ids = []

                    # Migrate state written by the former one-message-per-channel
                    # publisher without replacing its existing Discord message.
                    legacy_message_id = str(saved_post.get("message_id", ""))
                    if not saved_message_ids and legacy_message_id.isdigit():
                        saved_message_ids = [legacy_message_id]

                    existing_messages: list[discord.Message] = []
                    if str(saved_post.get("channel_id", "")) == str(channel_id):
                        for saved_message_id in saved_message_ids:
                            message_id = str(saved_message_id)
                            if not message_id.isdigit():
                                continue
                            try:
                                message = await channel.fetch_message(int(message_id))
                            except discord.NotFound:
                                continue
                            if self.bot.user is not None and message.author.id == self.bot.user.id:
                                existing_messages.append(message)

                    synced_messages: list[discord.Message] = []
                    created_count = 0
                    updated_count = 0
                    for index, embed in enumerate(embeds):
                        if index < len(existing_messages):
                            message = existing_messages[index]
                            await message.edit(
                                content=None,
                                embed=embed,
                                allowed_mentions=discord.AllowedMentions.none(),
                            )
                            updated_count += 1
                        else:
                            message = await channel.send(
                                embed=embed,
                                allowed_mentions=discord.AllowedMentions.none(),
                            )
                            created_count += 1
                        synced_messages.append(message)

                    deleted_count = 0
                    for stale_message in existing_messages[len(embeds):]:
                        await stale_message.delete()
                        deleted_count += 1

                    result_parts = []
                    if created_count:
                        result_parts.append(f"created {created_count}")
                    if updated_count:
                        result_parts.append(f"updated {updated_count}")
                    if deleted_count:
                        result_parts.append(f"removed {deleted_count} old")
                    results[post_name] = ", ".join(result_parts) or "unchanged"

                    post_state[post_name] = {
                        "channel_id": str(channel_id),
                        "message_ids": [str(message.id) for message in synced_messages],
                    }
                    save_json(POSTS_FILE, post_state)
                except (discord.DiscordException, TypeError) as error:
                    results[post_name] = f"failed: {error}"

            return results

    @commands.Cog.listener()
    async def on_ready(self):
        results = await self._sync_posts()
        LOGGER.info("Recruitment information sync: %s", results)

    @app_commands.command(name="publish-recruitment-info", description="Create or update the recruitment information posts")
    async def publish_recruitment_info(self, interaction: discord.Interaction):
        if not await require_recruitment_staff(interaction):
            return
        await interaction.response.defer(ephemeral=True)
        results = await self._sync_posts()
        summary = "\n".join(
            f"**{name.replace('_', ' ').title()}:** {status}"
            for name, status in results.items()
        )
        await interaction.followup.send(summary, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(RecruitmentInformation(bot))
