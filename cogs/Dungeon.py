import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import time
import asyncio
import re

class Dungeon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot;

    @commands.Cog.listener()
    async def on_ready(self):
        print("dungeons is ready")

    def scrape_wiki(self, url):
        if url == "https://lostark.wiki.fextralife.com/King+Luterra's+Tomb":
            url = "https://lostark.wiki.fextralife.com/Tomb+of+the+Great+King+Luterra"
        print("Loading URL:", url)
        options = Options()
        options.add_argument("--headless=old")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36") # bypass cloudflare stuff

        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(2) #wait for website to load

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        tables = soup.find_all('table', attrs={'class': 'wiki_table'})[0].find('tbody').find_all('tr')
        section_data = []

        level = 0
        players = 0
        image_link = None

        base_url = "https://lostark.wiki.fextralife.com"
        for tr in tables:
            category = tr.find('td').find('strong')
            text = tr.find('td', attrs={'style': 'text-align: center;'})

            if category and text:
                category = category.get_text()
                text = text.get_text()
                if "Entry Requirement" in category:
                    item_level = re.search(r'(Item Level \d+)', text)
                    if item_level:
                        item_level = item_level.group(1)
                        level = item_level
                elif "Players" in category:
                    players = text
            
            if level == 0 or players == 0:
                continue
            else:
                break

        for tr in tables:
            image = tr.find('td', attrs={'colspan': '2'}).find('p').find('img')
            if image:
                image_link = base_url + image.get('src')
                break
        section_data.append({
            'level': level,
            'players': players,
            'image': image_link
        })

        print(section_data)
        return section_data

    @commands.command()
    async def dungeon(self, ctx, *, dungeonName:str):
        try:
            file = open("./cogs/locations.json")
            data = json.load(file)
        except FileNotFoundError:
            await ctx.send("The JSON file was not found.")
            return
        except json.JSONDecodeError:
            await ctx.send("The JSON file is not properly formatted.")
            return

        url = "https://lostark.wiki.fextralife.com/"
        current_dungeon = None
        current_roster = []
        keys = data.keys()
        queries = []

        for key in keys:
            if dungeonName in key and "[dungeon]" in key:
                current_dungeon = key
                adjusted_name = key
                adjusted_name = ' '.join(word.capitalize() for word in adjusted_name.split())
                adjusted_name = adjusted_name.replace(" ", "+") #replace spaces
                adjusted_name = adjusted_name[:-10]
                queries.append(adjusted_name)

        if len(queries) > 1:
            await ctx.send(f"> **Your query is too vague. Did you mean:**")
            for key in keys:
                if dungeonName in key:
                    await ctx.send(f"> **{key.upper()}?**")
            return

        url += queries[0] #adjusted location name

        if current_dungeon is None:
            await ctx.send(f"> **{dungeonName.upper()} is not a valid dungeon.**")
            return

        current_roster.append(ctx.author.display_name)
        
        buffer = await ctx.send("> **Loading...**")
        info = self.scrape_wiki(url)
        await buffer.delete()
        
        if not info:
            await ctx.send("> **An error has occurred.**")

        def create_embed():
            new_roster = "\n".join(current_roster)
            embed = discord.Embed(
                title="Dungeon Alert ⚔️",
                color=0x71368a
            )
            #embed.set_image(url="")
            embed.add_field(
                name=f"{(ctx.author.display_name).upper()} wants to start a(n) {current_dungeon.upper()[:-10]} run!",
                value="",
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
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            return embed

        message = await ctx.send(embed=create_embed())

        await message.add_reaction("👍")
        await message.add_reaction("👎")

        def check_add(reaction, user):
            return user and str(reaction.emoji) in "👍, 👎" and reaction.message.id == message.id
    
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check_add)

                if user.id != ctx.author.id and len(current_roster) < 4 and reaction.emoji == "👍" and user.display_name not in current_roster:
                    current_roster.append(user.display_name)
                    await message.edit(embed=create_embed())
                    await ctx.send(f"> **{user.display_name} has joined the {current_dungeon.upper()[:-10]} party!**")
                elif reaction.emoji == "👍" and user.display_name in current_roster:
                    await ctx.send(f"> **You are already in the {current_dungeon.upper()[:-10]} party, {user.display_name}!**")
                elif reaction.emoji == "👍" and len(current_roster) > 4:
                    await ctx.send(f"> **Sorry {user.display_name}, the {current_dungeon.upper()[:-10]} party is full!**")
                elif user.id != ctx.author.id and reaction.emoji == "👎" and user.display_name in current_roster:
                    current_roster.remove(user.display_name)
                    await message.edit(embed=create_embed())
                    await ctx.send(f"> **{user.display_name} has left the party!**")
                await reaction.remove(user)
            
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break

async def setup(bot):
    await bot.add_cog(Dungeon(bot))
