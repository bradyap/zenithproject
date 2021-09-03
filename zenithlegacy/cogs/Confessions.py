import discord
from auth import auth
from discord.ext import commands
import os
from discord.ext.commands import CommandNotFound
from discord_slash import SlashCommand
import json
from datetime import datetime
import asyncio

#os path 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#utility functions
async def confessMuteTimer(id, time):
    global confessLogs
    global confessMuted
    time = time * 3600
    await asyncio.sleep(time)
    confessMuted.remove(confessLogs.get(id))

class Confessions(commands.Cog, description="Anonymous confessions. Requires level 2."):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Configures confessions (level 2 required)", description="Configures confessions (level 2 required).")
    async def confessions(self, ctx, *args):
        await ctx.send("Cog working.")

def setup(bot):
    bot.add_cog(Confessions(bot))