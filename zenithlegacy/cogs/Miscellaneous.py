import discord
from auth import auth
from discord.ext import commands
import resources
import random
import os

#os path 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class Miscellaneous(commands.Cog, description="Uncategorized commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Returns schedule for specified school (hhs, slhs)", description="Returns schedule for specified school (hhs, slhs).")
    async def bell(self, ctx, school, *args):
        input = " ".join(args[:])
        if school == "hhs" or school == "HHS":
            if input == "2hr" or input == "early release":
                await ctx.send(file=discord.File("../content/hhs2hr.png"))
            else:
                await ctx.send(file=discord.File("../content/hhs.png"))
        elif school == "slhs" or school == "SLHS":
            if input == "2hr" or input == "early release":
                await ctx.send(file=discord.File("../content/slhs2hr.png"))
            else:
                await ctx.send(file=discord.File("../content/slhs.png"))
        elif school == "temp":
            await ctx.send(file=discord.File("../content/temp.png"))
    
    @commands.command(brief="Adds vote to previous message", description="Adds vote to previous message.")
    async def poll(self, ctx):
        emotes = ['👍', '👎']
        msg = await ctx.channel.history(limit=2).flatten()
        await msg[0].delete()
        for emote in emotes:
            await msg[1].add_reaction(emote)
                
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == "?":
            emotes = ['👍', '👎']
            msg = await message.channel.history(limit=1).flatten()
            for emote in emotes:
                await msg[0].add_reaction(emote)

def setup(bot):
    bot.add_cog(Miscellaneous(bot))