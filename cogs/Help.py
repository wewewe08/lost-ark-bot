import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot;
        self.bot.remove_command('help')

    @commands.Cog.listener()
    async def on_ready(self):
        print("help is ready")
    
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="List of Commands",
            color=0xFFFFFF
        )

        embed.add_field(
            name="**!builds**",
            value="*lists all available builds on the maxroll.com website*",
            inline=False
        )

        embed.add_field(
            name="**!findbuild (class)**",
            value="*lists all available builds for a specific class*\nex: !findbuild berserker",
            inline=False
        )

        embed.add_field(
            name="**!mokoko (location name)**",
            value="*shows a map of all mokoko locations*\nex: !mokoko prideholme",
            inline=False
        )

        embed.add_field(
            name="**!dungeon (dungeon name) (date MM-DD) (time HH-MM) (am/pm)**",
            value="*schedules a dungeon run and allows you to create a party*\nex: !dungeon toxiclaw 09-26 7:00 pm",
            inline=False
        )

        embed.set_image(url="https://media1.tenor.com/m/oRVXTJsgYUcAAAAd/lostark-funny.gif")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))