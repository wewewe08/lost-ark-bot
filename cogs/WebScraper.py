import discord
from discord.ext import commands
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time, re

class WebScraper(commands.Cog):
    options = Options()
    options.add_argument("--headless=old")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36") # bypass cloudflare stuff

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("webscraper is ready")

    def scrape_maxroll_builds(self):
        url = 'https://maxroll.gg/lost-ark/category/build-guides' 

        driver = webdriver.Chrome(options=WebScraper.options)
        driver.get(url)
        time.sleep(1) #wait for website to load
        
        last_height = driver.execute_script("return document.body.scrollHeight") #check where you are on the page
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
        return builds
    
    def scrape_wiki(self, url):
        if url == "https://lostark.wiki.fextralife.com/King+Luterra's+Tomb":
            url = "https://lostark.wiki.fextralife.com/Tomb+of+the+Great+King+Luterra" 
        driver = webdriver.Chrome(options=WebScraper.options)
        driver.get(url)
        time.sleep(1) #wait for website to load

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

async def setup(bot):
    await bot.add_cog(WebScraper(bot))