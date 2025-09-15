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
        if member:
            score = self.scores[member.id]
            await ctx.send(
                f"📊 **{member.display_name}'s Scramble Score**\nWins: {score['wins']} | Losses: {score['losses']}"
            )
        else:
            if not self.scores:
                await ctx.send("📊 No scramble games played yet!")
                return
            top_players = sorted(
                self.scores.items(), key=lambda x: x[1]["wins"], reverse=True
            )[:5]
            desc = "\n".join(
                [
                    f"**{ctx.guild.get_member(uid).display_name}** — Wins: {score['wins']}, Losses: {score['losses']}"
                    for uid, score in top_players
                    if ctx.guild.get_member(uid)
                ]
            )
            await ctx.send(f"📊 **Top Scramble Players**\n{desc}")


async def setup(bot):
    await bot.add_cog(WordScramble(bot))
