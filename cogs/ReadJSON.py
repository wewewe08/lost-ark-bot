import discord
from discord.ext import commands
import json

class ReadJSON(commands.Cog):
    def __init__(self, bot):
        self.bot = bot;

    @commands.Cog.listener()
    async def on_ready(self):
        print("readJSON is ready")

    def get_data(self, file_path):
        try:
            file = open(file_path)
            data = json.load(file)
            return data
        except FileNotFoundError:
            print("JSON file not found")
            return None
        except json.JSONDecodeError:
            print("incorrect format")
            return None

async def setup(bot):
    await bot.add_cog(ReadJSON(bot))