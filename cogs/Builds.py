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

    def scrape_maxroll_builds(self):
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
        builds = self.scrape_maxroll_builds()

        if not builds:
            await ctx.send("No builds found or an error occurred.")
            return

        builds_per_page = 5
        pages = [builds[i:i + builds_per_page] for i in range(0, len(builds), builds_per_page)]

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