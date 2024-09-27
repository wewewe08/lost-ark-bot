import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import time
import asyncio
import re, os
from datetime import datetime
import pytz

class Dungeon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot;

    @commands.Cog.listener()
    async def on_ready(self):
        print("dungeons is ready")

    @commands.command()
    async def dungeon(self, ctx, *, text:str):
        #cogs
        schedule_cog = self.bot.get_cog("Schedule")
        json_cog = self.bot.get_cog("ReadJSON")
        webscraper_cog =  self.bot.get_cog("WebScraper")

        split_text = text.split(" ") #split arguments
        dungeonName = " ".join(split_text[:-3])
        datetime_str = " ".join(split_text[-3:])

        event_time = schedule_cog.check_valid_format(datetime_str)
        if  event_time == False:
            await ctx.send(f"> **Invalid format! Command usage: !dungeon (name) (MM-DD for the date) (HH:MM am/pm for the time)**")
            return
        else:
            epoch_time = schedule_cog.convert_epoch(event_time)

        dungeons = json_cog.get_data("./cogs/dungeons.json")
        if dungeons == None:
            await ctx.send("> **Something went wrong.**")
            return

        url = "https://lostark.wiki.fextralife.com/"
        current_dungeon = None
        party_members = []
        user_ids = []

        dungeon_names = dungeons.keys()
        queries = []

        for key in dungeon_names:
            if dungeonName in key and "[dungeon]" in key:
                current_dungeon = key
                adjusted_name = key
                adjusted_name = ' '.join(word.capitalize() for word in adjusted_name.split())
                adjusted_name = adjusted_name.replace(" ", "+") #replace spaces
                adjusted_name = adjusted_name[:-10]
                queries.append(adjusted_name)

        if len(queries) > 1:
            await ctx.send(f"> **Your query is too vague. Did you mean:**")
            for key in dungeon_names:
                if dungeonName in key:
                    await ctx.send(f"> **{key.upper()}?**")
            return

        url += queries[0] #adjusted location name when there's only 1 query

        if current_dungeon is None:
            await ctx.send(f"> **{dungeonName.upper()} is not a valid dungeon.**")
            return

        party_members.append(ctx.author.display_name)
        user_ids.append(ctx.author.id)
        buffer = await ctx.send("> **Loading...**")
        info = webscraper_cog.scrape_wiki(url)
        await buffer.delete()
        
        if info == []:
            await ctx.send("> **An error has occurred.**")

        def create_embed():
            discriminator = ctx.author.discriminator
            default_avatar_url = f'https://cdn.discordapp.com/embed/avatars/{int(discriminator) % 5}.png'

            new_roster = "\n".join(party_members)
            embed = discord.Embed(
                title="Dungeon Alert ⚔️",
                color=0x71368a
            )

            embed.add_field(
                name=f"{(ctx.author.display_name).upper()} wants to start a(n) {current_dungeon.upper()[:-10]} run!",
                value=f"*Starts: <t:{epoch_time}>*",
                inline=False
            )

            embed.add_field(
                name="Current party:",
                value=new_roster,
                inline=True
            )
            embed.add_field(
                name="Recommended Level:",
                value=f"{info[0]['level']}",
                inline=True
            )
            embed.add_field(
                name="Number of players:",
                value=f"{info[0]['players']}",
                inline=True
            )

            for key in dungeon_names:
                if dungeonName in key:
                    if dungeons[key] == "": break
                    embed.set_image(url=dungeons[key])

            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else default_avatar_url) # check for profile image
            return embed

        message = await ctx.send(embed=create_embed())

        await message.add_reaction("👍")
        await message.add_reaction("👎")

        def check_add(reaction, user):
            return user and str(reaction.emoji) in "👍, 👎" and reaction.message.id == message.id
    
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check_add)
                if user.id != ctx.author.id and len(user_ids) < 4 and reaction.emoji == "👍" and user.id not in user_ids:
                    party_members.append(user.display_name)
                    user_ids.append(user.id)
                    await message.edit(embed=create_embed())
                    await ctx.send(f"> **{user.display_name} has joined the {current_dungeon.upper()[:-10]} party!**")
                elif reaction.emoji == "👍" and user.id in user_ids:
                    await ctx.send(f"> **You are already in the {current_dungeon.upper()[:-10]} party, {user.display_name}!**")
                elif reaction.emoji == "👍" and len(user_ids) > 4 and user.id not in user_ids:
                    await ctx.send(f"> **Sorry {user.display_name}, the {current_dungeon.upper()[:-10]} party is full!**")
                elif user.id != ctx.author.id and reaction.emoji == "👎" and user.id in user_ids:
                    party_members.remove(user.display_name)
                    user_ids.remove(user.id)
                    await message.edit(embed=create_embed())
                    await ctx.send(f"> **{user.display_name} has left the party!**")
                await reaction.remove(user)
            
            except asyncio.TimeoutError:
                await message.clear_reactions()
                if schedule_cog is not None:
                    await schedule_cog.schedule_task(ctx, user_ids, queries[0], event_time)
                break

async def setup(bot):
    await bot.add_cog(Dungeon(bot))