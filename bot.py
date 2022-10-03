import os

import discord
from pycord.multicog import apply_multicog


class Memer(discord.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents, member_cache_flags=discord.MemberCacheFlags.from_intents(intents))

        self.token = os.environ['DISCORD_TOKEN']
        self.owners = [717408952035573767]
            
    async def on_ready(self):
        print("hi im savage.")

    def run(self):
        super().run(self.token)

bot = Memer()

cogs = ['donor', 'transfer']
for cog in cogs:
    try:
        bot.load_extension(cog)
        print(f"Loaded {cog}")
    except Exception as e:
        print(f"Failed to load {cog}: {e}")

apply_multicog(bot)

bot.run()