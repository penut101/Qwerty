# This is a cog for the Qwerty Bot
# It contains a word scramble game that users can play
# Written by Aiden Nemeroff

import discord
from discord.ext import commands
import random
import json
import os
from collections import defaultdict

WORDS = [
    "python",
    "discord",
    "scramble",
    "fraternity",
    "brotherhood",
    "computer",
    "pittsburgh",
    "programming",
    "challenge",
    "development",
    "community",
    "university",
    "education",
    "technology",
    "innovation",
    "collaboration",
    "leadership",
    "creativity",
    "teamwork",
    "excellence",
    "achievement",
    "success",
    "motivation",
    "inspiration",
    "determination",
]
SCORE_FILE = "scramble_scores.json"


class WordScramble(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}  # {channel_id: {"word": str, "scrambled": str}}
        self.scores = defaultdict(lambda: {"wins": 0, "losses": 0})
        self.load_scores()

    # -------------------- JSON Persistence --------------------
    def load_scores(self):
        if os.path.exists(SCORE_FILE):
            try:
                with open(SCORE_FILE, "r") as f:
                    data = json.load(f)
                    self.scores.update({int(k): v for k, v in data.items()})
            except Exception as e:
                print(f"Error loading scramble scores: {e}")

    def save_scores(self):
        try:
            with open(SCORE_FILE, "w") as f:
                json.dump(self.scores, f, indent=4)
        except Exception as e:
            print(f"Error saving scramble scores: {e}")

    # -------------------- Game Logic --------------------
    def scramble_word(self, word):
        letters = list(word)
        random.shuffle(letters)
        return "".join(letters)

    # !scramble - Starts a new game
    @commands.command()
    async def scramble(self, ctx):
        """Start a word scramble game"""
        if ctx.channel.id in self.active_games:
            await ctx.send("⚠️ A scramble is already active in this channel!")
            return

        word = random.choice(WORDS)
        scrambled = self.scramble_word(word)
        self.active_games[ctx.channel.id] = {"word": word, "scrambled": scrambled}

        await ctx.send(
            f"🔀 **Unscramble this word:** `{scrambled}`\nSolve it with `!unscramble <word>`!"
        )

    # !unscramble <word> - Attempt to solve the scramble
    @commands.command()
    async def unscramble(self, ctx, *, attempt: str):
        """Attempt to solve the word scramble"""
        if ctx.channel.id not in self.active_games:
            await ctx.send(
                "❌ No active scramble in this channel. Start one with `!scramble`."
            )
            return

        game = self.active_games[ctx.channel.id]
        word = game["word"]

        if attempt.lower().strip() == word.lower():
            self.scores[ctx.author.id]["wins"] += 1
            self.save_scores()
            await ctx.send(
                f"🎉 {ctx.author.mention} solved it! The word was **{word}**."
            )
            del self.active_games[ctx.channel.id]
        else:
            self.scores[ctx.author.id]["losses"] += 1
            self.save_scores()
            await ctx.send(f"❌ Nope, `{attempt}` isn’t correct. Try again!")

    # !scramblescore [@member] - Show scoreboard
    @commands.command()
    async def scramblescore(self, ctx, member: discord.Member = None):
        """Show Word Scramble scoreboard"""
        member = member or ctx.author

        # If specific member
        if member.id in self.scores:
            score = self.scores[member.id]
            total_games = score["wins"] + score["losses"]
            win_rate = (
                round((score["wins"] / total_games) * 100, 2) if total_games > 0 else 0
            )

            embed = discord.Embed(
                title=f"📊 Word Scramble Stats for {member.display_name}",
                color=discord.Color.blue(),
            )
            embed.add_field(name="🏆 Wins", value=score["wins"], inline=True)
            embed.add_field(name="❌ Losses", value=score["losses"], inline=True)
            embed.add_field(name="📈 Win Rate", value=f"{win_rate}%", inline=True)

            await ctx.send(embed=embed)

        # If no member specified → show top players
        else:
            if not self.scores:
                await ctx.send("📉 No scramble games played yet!")
                return

            top_players = sorted(
                self.scores.items(), key=lambda x: x[1]["wins"], reverse=True
            )[:5]

            embed = discord.Embed(
                title="🏅 Top Word Scramble Players", color=discord.Color.gold()
            )

            for rank, (uid, score) in enumerate(top_players, 1):
                member = ctx.guild.get_member(uid)
                if member:
                    total_games = score["wins"] + score["losses"]
                    win_rate = (
                        round((score["wins"] / total_games) * 100, 2)
                        if total_games > 0
                        else 0
                    )
                    embed.add_field(
                        name=f"#{rank} — {member.display_name}",
                        value=(
                            f"🏆 Wins: {score['wins']}\n"
                            f"❌ Losses: {score['losses']}\n"
                            f"📈 Win Rate: {win_rate}%"
                        ),
                        inline=False,
                    )

            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(WordScramble(bot))
