import discord
from discord.ext import commands
import json
import os

class Mokoko(commands.Cog):
    def __init__(self,bot):
        self.bot = bot;

    @commands.Cog.listener()
    async def on_ready(self):
        print("mokoko is ready")

    @commands.command()
    async def mokoko(self, ctx, *, place_name: str):
        try:
            file = open("./cogs/locations.json")
            data = json.load(file)
        except FileNotFoundError:
            await ctx.send("The JSON file was not found.")
            return
        except json.JSONDecodeError:
            await ctx.send("The JSON file is not properly formatted.")
            return

        keys = data.keys()
        keyName = None

        names = []
        for key in keys:
            if place_name.lower() in key:
                names.append(key)
                keyName = key

        if keyName is None:
            await ctx.send(f"No Mokoko Seeds found for '{place_name.upper()}'.") 
            return
        
        if len(names) > 1:
            await ctx.send(f"> Your query is too vague. Did you mean:")
            for name in names:
                await ctx.send(f"> {name.upper()}?")
            return

        embed = discord.Embed(
            title=f"Mokoko Seeds 🌱", 
            color=0x77DD77
        )

        embed.add_field(
            name=f"Seed Locations for {keyName.upper()}", 
            value="", 
            inline=False
        )

        embed.set_image(url=data[keyName])
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Mokoko(bot))