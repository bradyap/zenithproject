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

    @commands.command(brief="Sends a pickup line", description="Sends a pickup line.")
    async def pickup(self, ctx, member:discord.Member):
        line = random.choice(resources.pickupLines).replace("{name}", member.mention).replace("{author}", ctx.author.mention)
        await ctx.send(line)

    @commands.command(brief="Returns schedule for specified school (hhs, slhs)", description="Returns schedule for specified school (hhs, slhs).")
    async def bell(self, ctx, school, *args):
        input = " ".join(args[:])
        if school == "hhs" or school == "HHS":
            if input == "2hr" or input == "early release":
                await ctx.send(file=discord.File("./images/hhs2hr.png"))
            else:
                await ctx.send(file=discord.File("./images/hhs.png"))
        if school == "slhs" or school == "SLHS":
            if input == "2hr" or input == "early release":
                await ctx.send(file=discord.File("./images/slhs2hr.png"))
            else:
                await ctx.send(file=discord.File("./images/slhs.png"))

def setup(bot):
    bot.add_cog(Miscellaneous(bot))