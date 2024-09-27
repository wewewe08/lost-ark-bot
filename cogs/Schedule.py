import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import pytz

class Schedule(commands.Cog):
    def __init__(self,bot):
        self.bot = bot;

    @commands.Cog.listener()
    async def on_ready(self):
        print("schedule is ready")

    def check_valid_format(self, datetime_str):
        try:
            current_year = datetime.now().year
            full_datetime_str = f"{current_year}-{datetime_str}"
            event_time = datetime.strptime(full_datetime_str, '%Y-%m-%d %I:%M %p')
            return event_time
        except ValueError:
            return False
        
    def convert_epoch(self, event_time):
        local_tz = pytz.timezone("America/New_York")
        localized_datetime = local_tz.localize(event_time)
        utc_datetime = localized_datetime.astimezone(pytz.UTC)
        epoch_time = int(utc_datetime.timestamp())
        return epoch_time

    async def schedule_task(self, ctx, user_ids, dungeonName, event_time):
        present_time = datetime.now()
        delay = (event_time - present_time).total_seconds()
        print(f"starting delay of {delay}")
        await asyncio.sleep(delay)
        print("delay ended")
        for userid in user_ids:
            user = ctx.guild.get_member(userid)
            dungeonName = dungeonName.replace("+", " ")
            await ctx.send(f"> **{user.mention}, your {dungeonName.upper()} run is starting!**")

async def setup(bot):
    await bot.add_cog(Schedule(bot))