import discord
from auth import auth
from discord.ext import commands
import wolframalpha
import wikipedia
import re
from google.cloud import translate_v2 as translate
import resources
import os
import requests
import io
import random
from PIL import Image
from io import BytesIO

#os path 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#wolfram alpha
wclient = wolframalpha.Client(auth.appId)

#googletranslate
translate_client = translate.Client.from_service_account_json("../auth/DiscordBot-b0d16fb53e59.json")

class Content(commands.Cog, description="Deals with web content"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Asks Wolfram Alpha an inputted question", description="Asks Wolfram Alpha an inputted question. Some questions will not return results.")
    async def ask(self, ctx, *args):
        async with ctx.channel.typing():
            input = ' '.join(args[:])
            res = wclient.query(input)
            if res['@success'] == 'false':
                print(f'cmdAsk: Question cannot be resolved.')
                await ctx.send('Question cannot be resolved.')
            else:
                try:
                    result = res['pod'][1]['subpod']['img']['@src']
                    title = input
                    embed = discord.Embed(title=title)
                    embed.set_image(url=result)
                    await ctx.send(embed=embed)
                except:
                    result = next(res.results).text
                    await ctx.send(result)

    @commands.command(brief="Returns a Wikipedia page for the given term", description="Returns a Wikipedia page for the given term.")
    async def wiki(self, ctx, *args):
        async with ctx.channel.typing():
            input = ' '.join(args[:])
            res = wikipedia.search(input)
            if not res:
                await ctx.send('No response from wikipedia.')
            try:
                page = wikipedia.page(res[0])
            except wikipedia.exceptions.DisambiguationError as e:
                page =  wikipedia.page(e.options[0])
            title = page.title.encode('utf-8')
            summary = page.summary.encode('utf-8')
            title1 = title.decode('utf-8', 'ignore')
            summary1 = summary.decode('utf-8')
            link = page.url[:2000]
            embed = discord.Embed(title=title1, description=link)
            summary2 = re.split('(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', summary1)
            num = 0
            temp = summary2[num]
            printing = True
            while printing:
                if num < len(summary2):
                    while len(temp) <= 1024 and num < len(summary2):
                        if len(temp) + len(summary2[num]) <= 1024:
                            temp = temp + ' ' + summary2[num]
                            num = num + 1 
                        else:
                            embed.add_field(name='\u200b', inline=False, value=temp)
                            temp = ''
                            temp = summary2[num]
                            break
                else:
                    embed.add_field(name='\u200b', inline=False, value=temp)
                    printing = False
            await ctx.send(embed=embed)

    @commands.command(brief="Translates given text into given language", description="Translates given text into given language. See syntax below. Command autodetects source language.")
    async def translate(self, ctx, langInput, *input):
        async with ctx.channel.typing():
            langIn = langInput.capitalize()
            content = ' '.join(input[:])
            langs1 = dict((v,k) for k,v in resources.langs.items())
            langs2 = resources.langs
            lang = langs1.get(langIn, langIn)
            pLang = langs2.get(langIn, langIn)
            result = translate_client.translate(content, lang)
            og = langs2.get(result["detectedSourceLanguage"], "noneType")
            embed = discord.Embed(title=f"Translator")
            try:
                embed.add_field(name=f"Text translated from {og} to {pLang}.", value=result["translatedText"], inline=False)
            except:
                embed.add_field(name="Error", value="Translation error. Please try again.", inline=False)
            await ctx.send(embed=embed)

    @commands.command(brief="Fetches google results for given search term", description="Fetches google results for given search term.")
    async def search(self, ctx, *input):
        query = ' '.join(input[:])
        page = 1
        start = (page - 1) * 10 + 1
        url = f"https://www.googleapis.com/customsearch/v1?key={auth.searchApi}&cx={auth.searchEngineId}&q={query}&start={start}"
        data = requests.get(url).json()
        search_items = data.get("items")
        embed = discord.Embed(title="Results")
        for search_item in search_items:
            title = search_item.get("title")
            snippet = search_item.get("snippet")
            link = search_item.get("link")
            embed.add_field(name=title, inline=False, value=snippet + "\n" + link)
        await ctx.send(embed=embed)

    @commands.command(brief="Fetches image from google results for given search term", description="Fetches image from google results for given search term.")
    async def image(self, ctx, *input):
        query = ' '.join(input[:])
        page = 1
        start = (page - 1) * 10 + 1
        url = f"https://www.googleapis.com/customsearch/v1?key={auth.searchApi}&cx={auth.searchEngineId}&q={query}&start={start}&searchType=image"
        data = requests.get(url).json()
        search_items = data.get("items")
        search_item = random.choice(search_items)
        link = search_item.get("link")
        res = requests.get(link)
        image = Image.open(BytesIO(res.content)).convert('RGB')
        try: 
            with BytesIO() as imageBinary:
                image.save(imageBinary, 'PNG')
                imageBinary.seek(0)
                await ctx.send(file=discord.File(fp=imageBinary, filename='image.png'))
        except:
            newsize = (128, 128)
            image = image.resize(newsize)
            with BytesIO() as imageBinary:
                    image.save(imageBinary, 'PNG')
                    imageBinary.seek(0)
                    await ctx.send(file=discord.File(fp=imageBinary, filename='image.png'))

def setup(bot):
    bot.add_cog(Content(bot))