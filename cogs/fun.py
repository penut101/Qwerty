import discord
from discord.ext import commands
import random

class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.eight_ball_responses = [
            "Yes!", "Nope.", "Maybe...", "Definitely!", "Absolutely not.",
            "Ask again later.", "Without a doubt.", "I'm not sure.", "Signs point to yes."
        ]
        self.facts = [
            "Honey never spoils. Archaeologists have found 3,000-year-old jars of it still preserved!",
            "Bananas are berries, but strawberries aren't.",
            "A group of flamingos is called a 'flamboyance'.",
            "Octopuses have three hearts.",
            "The first email was sent by Ray Tomlinson to himself in 1971."
        ]
# !eightball - Ask the magic 8-ball a question
    @commands.command()
    async def eightball(self, ctx, *, question: str):
        """Ask the magic 8-ball a question."""
        response = random.choice(self.eight_ball_responses)
        await ctx.send(f"🎱 {response}")
# !fact - Get a random fun fact
    @commands.command()
    async def fact(self, ctx):
        """Get a random fun fact."""
        fact = random.choice(self.facts)
        await ctx.send(f"📚 Fun Fact: {fact}")
# !vibecheck - Check if you pass the vibe check
    @commands.command()
    async def vibecheck(self, ctx):
        """Check if you pass the vibe check."""
        passed = random.choice([True, False])
        if passed:
            await ctx.send("✅ You passed the vibe check!")
        else:
            await ctx.send("❌ You failed the vibe check. Better luck next time!")
# !coinflip - Flip a coin
    @commands.command()
    async def coinflip(self, ctx):
        """Flip a coin."""
        result = random.choice(["Heads", "Tails"])
        await ctx.send(f"🪙 {result}")

async def setup(bot):
    await bot.add_cog(FunCog(bot))
