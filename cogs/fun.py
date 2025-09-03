# This is a cog for the Qwerty Bot
# It contains fun commands that users can interact with.
# Written by Aiden Nemeroff

# Needed dependencies:
# discord.py
import discord
from discord.ext import commands
import random
import asyncio
import time
import json
import os

class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Dictionary to hold the responses for the magic 8-ball and fun facts
        self.eight_ball_responses = [
            "Yes!", "Nope.", "Maybe...", "Definitely!", "Absolutely not.",
            "Ask again later.", "Without a doubt.", "I'm not sure.", "Signs point to yes."
        ]
        # Dictionary of fun facts to share
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
        "public static void main(String[] args) { System.out.println(\"Java!\"); }",
        "synchronized(lock) { counter++; notifyAll(); }",
        "Incomprehensibilities are often misunderstood.",
        "C:\\Users\\Admin\\Documents\\Projects\\TypeFight\\phrases.txt",
        "If two witches were watching two watches, which witch would watch which watch?",
        "The sixth sick sheikh's sixth sheep's sick.",
        "Beware the Jabberwock, my son! The jaws that bite, the claws that catch!",
        "Pneumonoultramicroscopicsilicovolcanoconiosis is the longest English word."
    ],
    "demon": [
        # Code / technical
        "for(int i=0; i<1000; i++){ System.out.printf(\"%d \", i); }",
        "const obj = {name: \"Qwerty\", skills: [\"typing\", \"python\", \"discord\"]};",
        "https://www.kappathetapi.org/events?ref=QWERTY&type=challenge&level=demon#typing",
        "rm -rf / --no-preserve-root",
        "function* generator(){yield* [1,2,3,4,5];}",
        "import re; print(re.findall(r'\\b[a-z]+\\b', 'This is demon level'))",
        "SELECT * FROM users WHERE username='admin' AND password='password123';",
        "0xDEADBEEFCAFEBABE",
        "sudo apt-get install libssl-dev build-essential python3-dev",
        # Tongue-twisters / hard sentences
        # Visual traps
        "lIlIlI",
        "O0Oo0O",
        "1lI1I1l",
        "qwertyytrewq",
        "asdfghjkl;';lkjhgfdsa",
    ]
}

        self.leaderboard_file = "typefight_leaderboard.json"

    # Load the leaderboard from a JSON file
    def load_leaderboard(self):
        if os.path.exists(self.leaderboard_file):
            with open(self.leaderboard_file, "r") as f:
                return json.load(f)
        return {}
    
    # Write to the leaderboard
    def save_leaderboard(self, data):
        with open(self.leaderboard_file, "w") as f:
            json.dump(data, f, indent=4)

    # Update the leaderboard with a user's win
    def update_leaderboard(self, user_id, username, level):
        data = self.load_leaderboard()
        if user_id not in data:
            data[user_id] = {"name": username, "easy": 0, "medium": 0, "hard": 0}
        data[user_id][level] += 1
        self.save_leaderboard(data)

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

# !typefight <difficulty> - Start a typing challenge
    @commands.command()
    async def typefight(self, ctx, level: str = "medium"):
        """Start a typing challenge at a given difficulty level."""
        level = level.lower()
        if level not in self.typefight_phrases:
            await ctx.send("❌ Invalid level! Use `easy`, `medium`, or `hard`.")
            return

        phrase = random.choice(self.typefight_phrases[level])
        await ctx.send(f"🎯 **{level.capitalize()} Mode**\n⌛ Get ready to type in 3 seconds...")
        await asyncio.sleep(3) # Wait for 3 seconds before starting the challenge
        await ctx.send(f"⚡ First to type: **`{phrase}`**")

        # Define a check function to verify the message
        def check(m):
            return m.channel == ctx.channel and m.content.strip() == phrase 

        try:
            start = time.time()
            msg = await self.bot.wait_for("message", check=check, timeout=30)
            end = time.time()
            duration = round(end - start, 2)
            await ctx.send(f"🏆 {msg.author.mention} wins in {duration} seconds!")

            self.update_leaderboard(str(msg.author.id), str(msg.author), level)

        except asyncio.TimeoutError:
            await ctx.send("⏱️ Time's up! No one typed it correctly.")

    # !typefightleaderboard <difficulty> - View the TypeFight leaderboard
    @commands.command()
    async def typefightleaderboard(self, ctx, level: str = "medium"):
        """View the top TypeFight players for a given difficulty."""
        level = level.lower()
        if level not in ["easy", "medium", "hard"]:
            await ctx.send("❌ Invalid level! Use `easy`, `medium`, or `hard`.")
            return

        data = self.load_leaderboard()
        sorted_data = sorted(
            data.items(),
            key=lambda x: x[1][level],
            reverse=True
        )

        if not sorted_data or all(user[1][level] == 0 for user in sorted_data):
            await ctx.send(f"📉 No wins recorded yet for `{level}` level.")
            return

        leaderboard = "\n".join(
            [f"**{i+1}.** {entry[1]['name']} — {entry[1][level]} win(s)"
             for i, entry in enumerate(sorted_data[:10])]
        )

        await ctx.send(
            f"🏆 **Top TypeFighters — {level.capitalize()}**\n\n{leaderboard}"
        )

    # !resettypefight - Reset the TypeFight leaderboard (Admin only)
    @commands.command(name="resettypefight")
    @commands.has_permissions(administrator=True)
    async def reset_typefight_leaderboard(self, ctx):
        """(Admin only) Reset the TypeFight leaderboard."""
        self.save_leaderboard({})
        await ctx.send("🧹 TypeFight leaderboard has been reset.")

async def setup(bot):
    await bot.add_cog(FunCog(bot))
