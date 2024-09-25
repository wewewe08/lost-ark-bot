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

    def scrape_maxroll_build(self, buildKeyword):
        url = 'https://maxroll.gg/lost-ark/category/build-guides' 

        options = Options()
        options.add_argument("--headless=old")

        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(1) #wait for website to load
        
        last_height = driver.execute_script("return document.body.scrollHeight") #check where you're on the page
        #load all builds
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") #scroll to the bottom
            time.sleep(1)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        builds = soup.find_all('div', attrs={'class': 'border-grey-extra'})
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
    async def findbuild(self, ctx, *, build: str):
        buffer = await ctx.send("> **Searching for builds...**")
        builds = self.scrape_maxroll_build(build)
        await buffer.delete()

        if not builds:
            await ctx.send("**No builds found or an error occurred.**")
            return

        for build in builds:
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