import os
from typing import Final
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

#startup
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type = discord.ActivityType.listening, name = "!help to list commands"))
    print("Bot is running.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.CheckFailure):
        await  ctx.send("> **you do not have permission to use this command.**")
        return

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())