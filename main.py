import os
from typing import Final
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

#startup
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type = discord.ActivityType.listening, name = "! prefix"))
    print("Bot is running.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.CheckFailure):
        await  ctx.send("> **you do not have permission to use this command.**")
        return

#cogs here
extensions = []
if __name__ == "__main__":
    for ext in extensions:
        bot.load_extension(ext)

bot.run(TOKEN)