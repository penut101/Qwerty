# Fun Cog for Qwerty Bot
# Contains fun commands (no TypeFight here)
# Written by Aiden Nemeroff

import discord
from discord.ext import commands
from discord import app_commands
import random


class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Magic 8-ball responses
        self.eight_ball_responses = [
            "Yes!",
            "Nope.",
            "Maybe...",
            "Definitely!",
            "Absolutely not.",
            "Ask again later.",
            "Without a doubt.",
            "I'm not sure.",
            "Signs point to yes.",
        ]
        # Fun facts
        self.facts = [
            "Honey never spoils. Archaeologists have found 3,000-year-old jars of it still preserved!",
            "Bananas are berries, but strawberries aren't.",
            "A group of flamingos is called a 'flamboyance'.",
            "Octopuses have three hearts.",
            "The first email was sent by Ray Tomlinson to himself in 1971.",
            "The Eiffel Tower can be 15 cm taller during the summer.",
            "Avocados are fruit, not vegetables.",
            "A day on Venus is longer than its year.",
            "Wombat poop is cube-shaped.",
            "Sharks existed before trees.",
            "A snail can sleep for three years.",
            "There are more stars in the universe than grains of sand on Earth.",
            "Cows have best friends and get stressed when they are separated.",
            "Sloths can hold their breath longer than dolphins can.",
            "The inventor of the frisbee was turned into a frisbee after he died.",
            "A jiffy is an actual unit of time: 1/100th of a second.",
            "The longest hiccuping spree lasted 68 years.",
            "Butterflies can taste with their feet.",
            "Koalas have fingerprints that are almost identical to human fingerprints.",
            "Scotland has 421 words for snow.",
            "Sea otters hold hands when they sleep to avoid drifting apart.",
            "Pineapples take about two years to grow.",
            "The heart of a shrimp is located in its head.",
            "The shortest war in history lasted 38 to 45 minutes.",
            "The unicorn is the national animal of Scotland.",
            "A small child could swim through the veins of a blue whale.",
            "Tigers have striped skin, not just striped fur.",
            "There's a basketball court on the top floor of the U.S. Supreme Court Building.",
            "Your nostrils only work one at a time.",
            "It's impossible to hum while holding your nose.",
            "A single strand of spaghetti is called a 'spaghetto'.",
            "Pteronophobia is the fear of being tickled by feathers.",
            "A crocodile can't stick its tongue out.",
            "Most wasabi consumed is not real wasabi but horseradish and food coloring.",
            "Some cats are allergic to humans.",
            "The dot on the letter 'i' is called a tittle.",
            "Humans share about 60% of their DNA with bananas.",
            "Octopuses have nine brains.",
        ]

    #!8ball <question> - Ask the magic 8-ball a question
    @app_commands.command(name="eightball", description="Ask the magic 8-ball a question")
    @app_commands.describe(question="The question to ask the magic 8-ball")
    async def eightball(self, interaction: discord.Interaction, question: str):
        """Ask the magic 8-ball a question."""
        response = random.choice(self.eight_ball_responses)
        await interaction.response.send_message(f"🎱 {response}")

    #!fact - Get a random fun fact
    @app_commands.command(name="fact", description="Get a random fun fact")
    async def fact(self, interaction: discord.Interaction):
        """Get a random fun fact."""
        fact = random.choice(self.facts)
        await interaction.response.send_message(f"📚 Fun Fact: {fact}")

    #!vibecheck - Check if you pass the vibe check
    @app_commands.command(name="vibecheck", description="Check if you pass the vibe check")
    async def vibecheck(self, interaction: discord.Interaction):
        """Check if you pass the vibe check."""
        passed = random.choice([True, False])
        if passed:
            await interaction.response.send_message("✅ You passed the vibe check!")
        else:
            await interaction.response.send_message("❌ You failed the vibe check. Better luck next time!")

    #!coinflip - Flip a coin
    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        """Flip a coin."""
        result = random.choice(["Heads", "Tails"])
        await interaction.response.send_message(f"🪙 {result}")


async def setup(bot):
    await bot.add_cog(FunCog(bot))
