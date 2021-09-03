from types import ClassMethodDescriptorType
import discord
from auth import auth
from discord.ext import commands
import asyncio
import random
import os
from datetime import datetime

#os path 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#utility functions
async def timerObject(ctx, time, user):
        await asyncio.sleep(time)
        await ctx.send(f"{user.mention}, your timer has expired.")

async def remindObject(ctx, time, user, input):
        await asyncio.sleep(time)
        await ctx.send(f"{user.mention}, {input}.")

class Utility(commands.Cog, description="Various utilities"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Returns mentioned user's id", description="Returns mentioned user's id. Defaults to message author.")
    async def id(self, ctx):
        try:
            userId = str(ctx.message.mentions[0].id)
        except:
            userId = str(ctx.message.author.id)
        await ctx.send("Mentioned user's ID is: " + userId + ".")

    @commands.command(brief="Flips a coin", description="Flips a coin.")
    async def coinflip(self, ctx):
        res = random.choice(["Heads.", "Tails."])
        await ctx.send(res)

    @commands.command(brief="Picks a random choice from a list of inputs separated by commas", description="Picks a random choice from a list of inputs separated by commas.")
    async def randomchoice(self, ctx, *args):
        choices = ' '.join(args[:]).split(',')
        res = random.choice(choices)
        await ctx.send(res)

    @commands.command(brief="Sets a timer for the specified amount of time", description="Sets a timer for the specified amount of time.", aliases=["t"])
    async def timer(self, ctx, time, unit):
        print(f"cmdTimer: Permission given ({ctx.author}).")
        user = ctx.message.author
        await ctx.send(f"Timer set for {time} {unit}.")
        if str(unit) == "second" or str(unit) == "seconds" or str(unit) == "sec" or str(unit) == "secs":
            time = int(time)
        elif str(unit) == "hour" or str(unit) == "hours" or str(unit) == "hr" or str(unit) == "hrs":
            time = int(time) * 3600
        elif str(unit) == "day" or str(unit) == "days":
            time = int(time) * 86400
        else:
            time = int(time) * 60
        await timerObject(ctx, time, user)

    @commands.command(brief="Reminds you to do something in a specified amount of time", description="Reminds you to do something in a specified amount of time.")
    async def remind(self, ctx, time, unit, *input):
        print(f"cmdTimer: Permission given ({ctx.author}).")
        input = ' '.join(input[:])
        user = ctx.message.author
        await ctx.send(f"Reminder set for {time} {unit} from now.")
        if str(unit) == "second" or str(unit) == "seconds" or str(unit) == "sec" or str(unit) == "secs":
            time = int(time)
        elif str(unit) == "hour" or str(unit) == "hours" or str(unit) == "hr" or str(unit) == "hrs":
            time = int(time) * 3600
        elif str(unit) == "day" or str(unit) == "days":
            time = int(time) * 86400
        else:
            time = int(time) * 60
        await remindObject(ctx, time, user, input)

    @commands.command(brief="Displays user information", description="Displays user information.")
    async def userinfo(self, ctx, member:discord.Member=None):
        if not member: member = ctx.message.author
        embed = discord.Embed(title="User Information", timestamp=datetime.now(), color=0x454599)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="Name", value=str(member))
        embed.add_field(name="Bot?", value=member.bot)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
        embed.set_footer(text="ID: " + str(member.id))
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Utility(bot))