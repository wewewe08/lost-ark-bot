import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio

class Schedule(commands.Cog):
    def __init__(self,bot):
        self.bot = bot;

    @commands.Cog.listener()
    async def on_ready(self):
        print("schedule is ready")

    async def schedule_task(self, ctx, userid_list, dungeonName, datetime_str):
        try:
            present_time = datetime.now()
            current_year = present_time.year
            full_datetime_str = f"{current_year}-{datetime_str}"
            event_time = datetime.strptime(full_datetime_str, '%Y-%m-%d %I:%M %p')

            delay = (event_time - present_time).total_seconds()
            await asyncio.sleep(delay)
            for userid in userid_list:
                user = ctx.guild.get_member(userid)
                dungeonName = dungeonName.replace("+", " ")
                await ctx.send(f"> **{user.mention}, your {dungeonName.upper()} run is starting!**")
        except ValueError:
            print("invalid format")

async def setup(bot):
    await bot.add_cog(Schedule(bot))