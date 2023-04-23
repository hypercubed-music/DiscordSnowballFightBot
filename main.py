import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

# bot = commands.Bot(command_prefix=['s!', 'S!'], intents=intents)


class SnowballHelp(commands.MinimalHelpCommand):
    async def send_bot_help(self, mapping):
        await self.get_destination().send(embed=discord.Embed(description="```s!collect: Lets the user collect a snowball\n\n"
                                          "s!throw [@user]: Throws a snowball at the targeted user\n\n"
                                          "s!stats: Shows the personal statistics of the user\n\n"
                                          "s!leaderboard: Shows the top 10 players who have hit/been hit```", color=0xcc3813))


class SnowballBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=['s!', 'S!'], intents=intents, help_command=SnowballHelp())
        self.initial_extensions = ['snowball']

    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)

    async def close(self):
        await super().close()

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="s!help ❄️"))
        print('Ready!')


if __name__ == "__main__":
    bot = SnowballBot()
    bot.run(TOKEN)