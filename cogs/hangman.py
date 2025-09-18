# This is a cog for the Qwerty Bot
# It contains a hangman game that users can play
# Written by Aiden Nemeroff

import discord
from discord.ext import commands
import random
from collections import defaultdict
import json
import os

# Word list
WORDS = [
    # Tech / Coding
    "python",
    "discord",
    "hangman",
    "computer",
    "programming",
    "algorithm",
    "database",
    "internet",
    "javascript",
    "software",
    # School / College
    "fraternity",
    "brotherhood",
    "pittsburgh",
    "university",
    "panthers",
    "library",
    "homework",
    "lecture",
    "science",
    "engineering",
    # Fun / General
    "football",
    "basketball",
    "friendship",
    "volcano",
    "rainbow",
    "diamond",
    "monster",
    "kitchen",
    "teacher",
    "music",
    "guitar",
    "piano",
    "chocolate",
    "adventure",
    "happiness",
]


# ASCII art for each stage
HANGMAN_PICS = [
    """
     +---+
         |
         |
         |
        ====""",
    """
     +---+
     O   |
         |
         |
        ====""",
    """
     +---+
     O   |
     |   |
         |
        ====""",
    """
     +---+
     O   |
    /|   |
         |
        ====""",
    """
     +---+
     O   |
    /|\\  |
         |
        ====""",
    """
     +---+
     O   |
    /|\\  |
    /    |
        ====""",
    """
     +---+
     O   |
    /|\\  |
    / \\  |
        ====""",
]

SCORE_FILE = "hangman_scores.json"


# -------------------- Hangman Cog --------------------
class Hangman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}  # {channel_id: game_data}
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
                print(f"Error loading scores: {e}")

    def save_scores(self):
        try:
            with open(SCORE_FILE, "w") as f:
                json.dump(self.scores, f, indent=4)
        except Exception as e:
            print(f"Error saving scores: {e}")

    # -------------------- Game Helpers --------------------
    def create_game(self, word, starter_id):
        return {
            "word": word,
            "guessed": set(),
            "wrong": 0,
            "max_wrong": len(HANGMAN_PICS) - 1,
            "starter": starter_id,
        }

    def display_word(self, word, guessed):
        return " ".join([letter if letter in guessed else "_" for letter in word])

    # -------------------- Commands --------------------

    # !hangman - Start a new game of Hangman
    @commands.command()
    async def hangman(self, ctx):
        """Start a new game of Hangman"""
        if ctx.channel.id in self.games:
            await ctx.send("⚠️ A game is already in progress in this channel!")
            return

        word = random.choice(WORDS)
        game = self.create_game(word, ctx.author.id)
        self.games[ctx.channel.id] = game

        await ctx.send(
            f"🎮 **Hangman started by {ctx.author.display_name}!** 🎮\n"
            f"{HANGMAN_PICS[0]}\n"
            f"Word: {self.display_word(word, game['guessed'])}\n"
            f"Guess letters with `!guess <letter>` or solve with `!solve <word>`."
        )

    # !guess <letter> - Guess a letter in Hangman
    @commands.command()
    async def guess(self, ctx, letter: str):
        """Guess a letter in Hangman"""
        if ctx.channel.id not in self.games:
            await ctx.send("❌ No active game here. Start one with `!hangman`.")
            return

        game = self.games[ctx.channel.id]
        word = game["word"]

        if len(letter) != 1 or not letter.isalpha():
            await ctx.send("⚠️ Please guess a single letter (a-z).")
            return

        letter = letter.lower()

        if letter in game["guessed"]:
            await ctx.send(f"⚠️ You already guessed `{letter}`!")
            return

        game["guessed"].add(letter)

        if letter in word:
            if all(l in game["guessed"] for l in word):
                self.scores[ctx.author.id]["wins"] += 1
                self.save_scores()
                await ctx.send(
                    f"✅ Correct! The word was **{word}**. {ctx.author.mention} wins! 🎉"
                )
                del self.games[ctx.channel.id]
            else:
                await ctx.send(
                    f"✅ Good guess!\n{self.display_word(word, game['guessed'])}"
                )
        else:
            game["wrong"] += 1
            if game["wrong"] >= game["max_wrong"]:
                self.scores[ctx.author.id]["losses"] += 1
                self.save_scores()
                await ctx.send(
                    f"{HANGMAN_PICS[game['wrong']]}\n"
                    f"❌ Wrong! Game over. The word was **{word}**. 💀"
                )
                del self.games[ctx.channel.id]
            else:
                await ctx.send(
                    f"{HANGMAN_PICS[game['wrong']]}\n"
                    f"❌ Wrong guess! ({game['wrong']}/{game['max_wrong']})\n"
                    f"{self.display_word(word, game['guessed'])}"
                )

    # !solve <word> - Try to solve the Hangman word
    @commands.command()
    async def solve(self, ctx, *, attempt: str):
        """Try to solve the Hangman word"""
        if ctx.channel.id not in self.games:
            await ctx.send("❌ No active game here. Start one with `!hangman`.")
            return

        game = self.games[ctx.channel.id]
        word = game["word"].lower()
        attempt = attempt.lower().strip()

        if attempt == word:
            self.scores[ctx.author.id]["wins"] += 1
            self.save_scores()
            await ctx.send(
                f"🎉 {ctx.author.mention} solved it! The word was **{word}** 🎉"
            )
            del self.games[ctx.channel.id]
        else:
            game["wrong"] += 1
            if game["wrong"] >= game["max_wrong"]:
                self.scores[ctx.author.id]["losses"] += 1
                self.save_scores()
                await ctx.send(
                    f"{HANGMAN_PICS[game['wrong']]}\n"
                    f"❌ Wrong solve attempt! Game over. The word was **{word}**. 💀"
                )
                del self.games[ctx.channel.id]
            else:
                await ctx.send(
                    f"{HANGMAN_PICS[game['wrong']]}\n"
                    f"❌ Nope, `{attempt}` isn’t the word. ({game['wrong']}/{game['max_wrong']})\n"
                    f"{self.display_word(word, game['guessed'])}"
                )

    # !hangmanscoreboard [@member] - Show scoreboard
    @commands.command()
    async def hangmanscoreboard(self, ctx, member: discord.Member = None):
        """Show Hangman scoreboard (overall or for a specific member)"""
        if member:
            score = self.scores[member.id]
            await ctx.send(
                f"📊 **{member.display_name}'s Hangman Score**\nWins: {score['wins']} | Losses: {score['losses']}"
            )
        else:
            if not self.scores:
                await ctx.send("📊 No games played yet!")
                return
            # Show top 5 players by wins
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
            await ctx.send(f"📊 **Top Hangman Players**\n{desc}")


async def setup(bot):
    await bot.add_cog(Hangman(bot))
