import discord
from discord.ext import commands
from datetime import datetime
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
        present_time_utc = datetime.now(pytz.UTC)
        event_time_utc = event_time.astimezone(pytz.UTC)
        offset = event_time_utc - present_time_utc
        new_event_time = present_time_utc.astimezone() + offset # convert to local timezone and add offset
        new_event_time_utc = new_event_time.astimezone(pytz.UTC) # convert back to UTC
        epoch_time = int(new_event_time_utc.timestamp())
        return epoch_time

    async def schedule_task(self, ctx, user_ids, dungeonName, event_time):
        present_time = datetime.now()
        delay = (event_time - present_time).totalseconds()
        print(f"waiting {delay} seconds")
        await asyncio.sleep(delay)
        for userid in user_ids:
            user = ctx.guild.get_member(userid)
            dungeonName = dungeonName.replace("+", " ")
            await ctx.send(f"> **{user.mention}, your {dungeonName.upper()} run is starting!**")

async def setup(bot):
    await bot.add_cog(Schedule(bot))