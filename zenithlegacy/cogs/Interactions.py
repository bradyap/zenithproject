import discord
from auth import auth
from discord.ext import commands
import resources
import random
import os
import json

#os path 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class Interactions(commands.Cog, description="Ping someone following the command."):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Sends a pickup line", description="Sends a pickup line.")
    async def pickup(self, ctx, member:discord.Member):
        line = random.choice(resources.pickupLines).replace("{name}", member.mention).replace("{author}", ctx.author.mention)
        await ctx.send(line)
    
    @commands.command(brief="Hug gifs", description="Hug gifs.")
    async def hug(self, ctx, member:discord.Member=None):
        if member is None:
            embed = discord.Embed(title="Zenith hugs " + ctx.message.author.display_name)
        else:
            embed = discord.Embed(title=ctx.message.author.display_name + " hugs " + member.display_name)
        filename = "../content/gif_links.json"
        with open (filename) as f:
            data = json.load(f)
        hug = random.choice(data["hug"])
        embed.set_image(url=hug)
        await ctx.send(embed=embed)
    
    @commands.command(brief="Kiss gifs", description="Kiss gifs.")
    async def kiss(self, ctx, member:discord.Member=None):
        if member is None:
            embed = discord.Embed(title="Zenith kisses " + ctx.message.author.display_name)
        else:
            embed = discord.Embed(title=ctx.message.author.display_name + " kisses " + member.display_name)
        filename = "../content/gif_links.json"
        with open (filename) as f:
            data = json.load(f)
        hug = random.choice(data["kiss"])
        embed.set_image(url=hug)
        await ctx.send(embed=embed)
    
    @commands.command(brief="Pat gifs", description="Pat gifs.")
    async def pat(self, ctx, member:discord.Member=None):
        if member is None:
            embed = discord.Embed(title="Zenith pats " + ctx.message.author.display_name)
        else:
            embed = discord.Embed(title=ctx.message.author.display_name + " pats " + member.display_name)
        filename = "../content/gif_links.json"
        with open (filename) as f:
            data = json.load(f)
        hug = random.choice(data["pat"])
        embed.set_image(url=hug)
        await ctx.send(embed=embed)
    
    @commands.command(brief="Slap gifs", description="Slap gifs.")
    async def slap(self, ctx, member:discord.Member=None):
        if member is None:
            embed = discord.Embed(title="Zenith slaps " + ctx.message.author.display_name)
        else:
            embed = discord.Embed(title=ctx.message.author.display_name + " slaps " + member.display_name)
        filename = "../content/gif_links.json"
        with open (filename) as f:
            data = json.load(f)
        hug = random.choice(data["slap"])
        embed.set_image(url=hug)
        await ctx.send(embed=embed)
    
    @commands.command(brief="Punch gifs", description="Punch gifs.")
    async def punch(self, ctx, member:discord.Member=None):
        if member is None:
            embed = discord.Embed(title="Zenith punches " + ctx.message.author.display_name)
        else:
            embed = discord.Embed(title=ctx.message.author.display_name + " punches " + member.display_name)
        filename = "../content/gif_links.json"
        with open (filename) as f:
            data = json.load(f)
        hug = random.choice(data["punch"])
        embed.set_image(url=hug)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Interactions(bot))