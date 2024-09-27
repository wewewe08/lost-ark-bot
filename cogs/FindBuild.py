from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import discord
from discord.ext import commands
import time
import asyncio

class FindBuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("findbuilds is ready")

    def load_builds(self, builds, buildKeyword):
        build_data = []

        for build in builds:
            titleWrapper = build.find('h2', attrs={'class': '_title_2sj5k_62'})
            title = (titleWrapper.text.strip()).lower()
            if buildKeyword.lower() in title:
                imagediv = build.find('div', attrs={'class': '_imageWrapper_2sj5k_35'})
                image = imagediv.find('img')['src']
                link = build.find('a')['href']

                build_data.append({
                    'title': title,
                    'link': link,
                    'image': image
                })
        return build_data

    @commands.command()
    async def findbuild(self, ctx, *, className: str):
        buffer = await ctx.send("> **Searching for builds...**")
        webscraper_cog = self.bot.get_cog("WebScraper")
        builds = webscraper_cog.scrape_maxroll_builds()
        loaded_builds = self.load_builds(builds, className)
        await buffer.delete()

        if loaded_builds == []:
            await ctx.send("**No builds found or an error occurred.**")
            return

        for build in loaded_builds:
            embed = discord.Embed(
                title="Maxroll Lost Ark Builds 📖", 
                color=0xFFD700
            )

            embed.add_field(
                name=f"{build['title'].upper()}", 
                value=f"[View Build](https://maxroll.gg{build['link']})", 
                inline=False
            )

            embed.set_image(url=build['image'])
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(FindBuild(bot))