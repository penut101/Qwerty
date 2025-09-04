# TypeFight Cog for Qwerty Bot
# Handles typing challenges, leaderboards, and stats
# Written by Aiden Nemeroff

import discord
from discord.ext import commands
import random
import asyncio
import time
import json
import os


class TypeFightCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.typefight_phrases = {
            "easy": [
                "hello",
                "discord",
                "bot",
                "python",
                "fast typing",
                "qwerty",
                "Coding is fun",
                "Type fast",
                "Practice makes perfect",
                "Hello, World!",
                "snail",
                "banana",
                "tangerine",
                "monkey",
                "pizza",
                "turtle",
                "slack",
                "Node.js",
            ],
            "medium": [
                "Macaroni and cheese",
                "You miss 100% of the shots you don't take",
                "A wild qwerty appears!",
                "Type this as fast as you can",
                "The quick brown fox jumps over the lazy dog",
                "Welcome to the TypeFight challenge!",
                "Kappa Theta Pi",
                "For the love of technology",
                "Fast fingers win the game",
                "Practice makes perfect",
                "Coding is fun",
                "Keep calm and type on",
                "Always commit your code",
                "The only limit is your imagination",
                "Python is a great programming language",
                "Hello, World! This is a typing challenge.",
                "Type this sentence as fast as you can",
                "Visual Studio Code",
                "Microsoft Surface Pro",
                "Teenage Mutant Ninja Turtles",
                "Why did the chicken cross the road?",
                "Hypertext Markup Language",
                "https://www.example.com",
            ],
            "hard": [
                "print('Hello, World!');",
                "It's not a bug, it's an undocumented feature.",
                "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
                "Supercalifragilisticexpialidocious",
                "Kappa Theta Pi is the best fraternity ever",
                "This bot was written in Python",
                "Qwerty was created by Aiden Nemeroff",
                "while(True): print('Never ending loop')",
                "The mitochondrion is the powerhouse of the cell.",
                "Antidisestablishmentarianism is a very long word.",
                "Sally sells seashells by the seashore quickly.",
                "Pseudo-pseudohypoparathyroidism is a rare disorder.",
                "The five boxing wizards jump quickly over the lazy dwarf.",
                'public static void main(String[] args) { System.out.println("Java!"); }',
                "synchronized(lock) { counter++; notifyAll(); }",
                "Incomprehensibilities are often misunderstood.",
                "C:\\Users\\Admin\\Documents\\Projects\\TypeFight\\phrases.txt",
                "If two witches were watching two watches, which witch would watch which watch?",
                "The sixth sick sheikh's sixth sheep's sick.",
                "Beware the Jabberwock, my son! The jaws that bite, the claws that catch!",
                "Pneumonoultramicroscopicsilicovolcanoconiosis is the longest English word.",
            ],
            "demon": [
                'for(int i=0; i<1000; i++){ System.out.println("This is difficult", i); }',
                "0xDEADBEEFCAFEBABE",
                "sudo apt-get install libssl-dev build-essential python3-dev",
                "asdfghjkl;';lkjhgfdsa",
                "Reminder: submit assignment before 11:59 PM EST.",
                "Look behind you... just kidding (or am I?)",
                "Press Ctrl+Alt+Delete only if absolutely necessary.",
                "Shopping list: eggs, milk, bread, cheese, apples, coffee.",
            ],
        }
        self.leaderboard_file = "typefight_leaderboard.json"

    # Load leaderboard
    def load_leaderboard(self):
        if os.path.exists(self.leaderboard_file):
            with open(self.leaderboard_file, "r") as f:
                return json.load(f)
        return {}

    # Save leaderboard
    def save_leaderboard(self, data):
        with open(self.leaderboard_file, "w") as f:
            json.dump(data, f, indent=4)

    # Update leaderboard
    def update_leaderboard(self, user_id, username, level, duration, won=True):
        data = self.load_leaderboard()
        if user_id not in data:
            data[user_id] = {
                "name": username,
                "easy": {
                    "wins": 0,
                    "time": 0.0,
                    "best": None,
                    "current_streak": 0,
                    "best_streak": 0,
                },
                "medium": {
                    "wins": 0,
                    "time": 0.0,
                    "best": None,
                    "current_streak": 0,
                    "best_streak": 0,
                },
                "hard": {
                    "wins": 0,
                    "time": 0.0,
                    "best": None,
                    "current_streak": 0,
                    "best_streak": 0,
                },
                "demon": {
                    "wins": 0,
                    "time": 0.0,
                    "best": None,
                    "current_streak": 0,
                    "best_streak": 0,
                },
            }

        stats = data[user_id][level]

        if won:
            stats["wins"] += 1
            stats["time"] += duration
            if stats["best"] is None or duration < stats["best"]:
                stats["best"] = duration
            stats["current_streak"] += 1
            if stats["current_streak"] > stats["best_streak"]:
                stats["best_streak"] = stats["current_streak"]
        else:
            stats["current_streak"] = 0

        self.save_leaderboard(data)

    # !typefight <difficulty> - Start a typing challenge
    @commands.command()
    async def typefight(self, ctx, level: str = "medium"):
        """Start a typing challenge."""
        level = level.lower()
        if level not in self.typefight_phrases:
            await ctx.send(
                "❌ Invalid level! Use `easy`, `medium`, `hard`, or `demon`."
            )
            return

        phrase = random.choice(self.typefight_phrases[level])
        await ctx.send(
            f"🎯 **{level.capitalize()} Mode**\n⌛ Get ready to type in 3 seconds..."
        )
        await asyncio.sleep(3)
        await ctx.send(f"⚡ First to type: **`{phrase}`**")

        def check(m):
            return m.channel == ctx.channel and m.content.strip() == phrase

        try:
            start = time.time()
            msg = await self.bot.wait_for("message", check=check, timeout=30)
            end = time.time()
            duration = round(end - start, 2)
            await ctx.send(f"🏆 {msg.author.mention} wins in {duration} seconds!")

            self.update_leaderboard(
                str(msg.author.id), str(msg.author), level, duration, won=True
            )
        except asyncio.TimeoutError:
            await ctx.send("⏱️ Time's up! No one typed it correctly.")
            self.update_leaderboard(
                str(ctx.author.id), str(ctx.author), level, 0, won=False
            )

    # !typefightleaderboard <difficulty> - View the leaderboard
    @commands.command()
    async def typefightleaderboard(self, ctx, level: str = "medium"):
        """View the TypeFight leaderboard."""
        level = level.lower()
        if level not in ["easy", "medium", "hard", "demon"]:
            await ctx.send(
                "❌ Invalid level! Use `easy`, `medium`, `hard`, or `demon`."
            )
            return

        data = self.load_leaderboard()
        sorted_data = sorted(
            data.items(), key=lambda x: x[1][level]["wins"], reverse=True
        )

        if not sorted_data or all(user[1][level]["wins"] == 0 for user in sorted_data):
            await ctx.send(f"📉 No wins recorded yet for `{level}` level.")
            return

        medals = ["🥇", "🥈", "🥉"]
        leaderboard_entries = []

        for i, entry in enumerate(sorted_data[:3]):
            leaderboard_entries.append(
                f"{medals[i]} **{entry[1]['name']}**\n"
                f"   🏆 Wins: {entry[1][level]['wins']}\n"
                f"   ⏱️ Avg Time: {round(entry[1][level]['time'] / entry[1][level]['wins'], 2)}s\n"
                f"   🔥 Best Streak: {entry[1][level]['best_streak']}\n"
            )

        for i, entry in enumerate(sorted_data[3:5], start=4):
            leaderboard_entries.append(
                f"**{i}. {entry[1]['name']}** — {entry[1][level]['wins']} win(s)"
            )

        leaderboard = "\n".join(leaderboard_entries)
        user_id = str(ctx.author.id)
        if user_id in data and data[user_id][level]["wins"] > 0:
            for rank, entry in enumerate(sorted_data, start=1):
                if entry[0] == user_id:
                    if rank > 5:
                        leaderboard += f"\n\n👤 You are ranked **#{rank}** with {data[user_id][level]['wins']} win(s)."
                    break
        await ctx.send(
            f"🏆 **Top TypeFighters — {level.capitalize()}**\n\n{leaderboard}"
        )

    # !typestats [@member] - View personal stats about a certain member or yourself
    @commands.command()
    async def typestats(self, ctx, member: discord.Member = None):
        """View personal TypeFight stats."""
        member = member or ctx.author
        data = self.load_leaderboard()

        if str(member.id) not in data:
            await ctx.send(f"📉 No stats recorded for {member.display_name}.")
            return

        user_stats = data[str(member.id)]
        embed = discord.Embed(
            title=f"📊 TypeFight Stats for {user_stats['name']}",
            color=discord.Color.green(),
        )

        for level in ["easy", "medium", "hard", "demon"]:
            stats = user_stats[level]
            if stats["wins"] > 0:
                avg_time = round(stats["time"] / stats["wins"], 2)
                embed.add_field(
                    name=level.capitalize(),
                    value=(
                        f"🏆 Wins: {stats['wins']}\n"
                        f"⏱️ Avg Time: {avg_time}s\n"
                        f"⚡ Best Time: {stats['best']}s\n"
                        f"🔥 Current Streak: {stats['current_streak']}\n"
                        f"💯 Best Streak: {stats['best_streak']}"
                    ),
                    inline=False,
                )
            else:
                embed.add_field(
                    name=level.capitalize(), value="No wins yet.", inline=False
                )

        await ctx.send(embed=embed)

    # !resettypefight - Reset the leaderboard but keep usernames (Admin only)
    @commands.command(name="resettypefight")
    @commands.has_permissions(administrator=True)
    async def reset_typefight_leaderboard(self, ctx):
        """(Admin only) Reset the TypeFight leaderboard but keep usernames."""
        data = self.load_leaderboard()

        for user_id, user_data in data.items():
            for level in ["easy", "medium", "hard", "demon"]:
                user_data[level] = {
                    "wins": 0,
                    "time": 0.0,
                    "best": None,
                    "current_streak": 0,
                    "best_streak": 0,
                }

        self.save_leaderboard(data)
        await ctx.send("🧹 TypeFight leaderboard has been reset!")


async def setup(bot):
    await bot.add_cog(TypeFightCog(bot))
