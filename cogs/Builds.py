from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import discord
from discord.ext import commands
import time
import asyncio

class Builds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("builds is ready")

    def load_builds(self, builds):
        build_data = []
        for build in builds:
            titlediv = build.find('div', attrs={'class': '_titleWrapper_2sj5k_62'})
            title = titlediv.find('h2').text.strip()
            link = build.find('a')['href']

            build_data.append({
                'title': title,
                'link': link,
            })
        return build_data

    @commands.command()
    async def builds(self, ctx):
        buffer = await ctx.send("> **Searching for builds...**")
        webscraper_cog = self.bot.get_cog("WebScraper")
        builds = webscraper_cog.scrape_maxroll_builds()
        loaded_builds = self.load_builds(builds)
        await buffer.delete()

        if not loaded_builds:
            await ctx.send("**No builds found or an error occurred.**")
            return

        builds_per_page = 5
        pages = [loaded_builds[i:i + builds_per_page] for i in range(0, len(loaded_builds), builds_per_page)]

        def create_embed(page_index):
            embed = discord.Embed(
                title=f"Maxroll Lost Ark Builds 📖", 
                color=0xFFD700
            )
            for build in pages[page_index]:
                embed.add_field(
                    name=build['title'], 
                    value=f"[View Build](https://maxroll.gg{build['link']})", 
                    inline=False
                )
                embed.set_footer(text=f"Page {page_index + 1}/{len(pages)}")
            return embed
        
        current_page = 0
        message = await ctx.send(embed=create_embed(current_page))

        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"] and reaction.message.id == message.id

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                if str(reaction.emoji) == "⬅️":
                    if current_page > 0:
                        current_page -= 1
                    else:
                        current_page = len(pages-1)
                    await message.edit(embed=create_embed(current_page))

                elif str(reaction.emoji) == "➡️":
                    if current_page < len(pages) - 1:
                        current_page += 1
                    else:
                        current_page = 0
                    await message.edit(embed=create_embed(current_page))
                await message.remove_reaction(reaction.emoji, user)
            
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break

async def setup(bot):
    await bot.add_cog(Builds(bot))