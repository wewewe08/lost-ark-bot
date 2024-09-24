import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import discord
from discord.ext import commands
import time

class Builds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("builds is ready")

    def scrape_maxroll_builds(self):
        url = 'https://maxroll.gg/lost-ark/category/build-guides' 
        driver = webdriver.Chrome()
        driver.get(url)
        time.sleep(1) #wait for website to load

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        
        builds = soup.find_all('div', attrs={'class': 'border-grey-extra'})

        build_data = []
        for build in builds:
            titlediv = build.find('div', attrs={'class': '_titleWrapper_2sj5k_62'})
            title = titlediv.find('h2').text.strip()
            link = build.find('a')['href']

            build_data.append({
                'title': title,
                'link': link
            })
        return build_data

    @commands.command()
    async def builds(self, ctx):
        builds = self.scrape_maxroll_builds()
        if builds:
            embed = discord.Embed(title="Maxroll Lost Ark Builds", color=0x00ff00)
            for build in builds:
                embed.add_field(name=build['title'], value=f"[View Build](https://maxroll.gg{build['link']})", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("No builds found or an error occurred.")

async def setup(bot):
    await bot.add_cog(Builds(bot))