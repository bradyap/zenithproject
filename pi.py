import os
import discord
import auth
from discord.errors import HTTPException
from discord.ext import commands
from notion.client import NotionClient
from threading import Timer
import subprocess
from datetime import datetime
from discord_slash import SlashCommand, SlashContext
from discord.utils import get
import subprocess
from discord.ext.commands import CommandNotFound
import asyncio

#os path 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#discord
bot = commands.Bot(command_prefix="$")
bot.remove_command('help')

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user) + " from " + auth.env + ".")
    print('----')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

@bot.command(hidden=True, brief="Returns bot state")
async def info(ctx):
    print(f"cmdInfo: Permission given ({ctx.message.author}).")
    await ctx.send('Pi logged in as {0} ({0.id})'.format(bot.user) + " from " + auth.env + ".")

@bot.command(hidden=True)
async def pExec(ctx, *args):
    input = " ".join(args[:])
    if ctx.message.author.id == auth.brady: 
        print(f"cmdExec: Permission given ({ctx.message.author}). Input = {input}.")
        stream = os.popen(input)
        output = stream.read()
        if output:
            await ctx.send(output)
        else:
            await ctx.send("No output.")
    else: 
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdAdd: Permission denied ({ctx.message.author}). Input = {input}.")

@bot.command(hidden=True)
async def pStatus(ctx, service):
    if ctx.message.author.id == auth.brady: 
        print(f"cmdStatus: Permission given ({ctx.message.author}).")
        stream = os.popen("sudo systemctl status " + service + " --no-pager -l --lines=3")
        output = stream.read()
        if output:
            await ctx.send(output)
        else:
            await ctx.send("No output.")
    else: 
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdAdd: Permission denied ({ctx.message.author}).")

@bot.command(hidden=True)
async def pRestart(ctx, service):
    if ctx.message.author.id == auth.brady: 
        print(f"cmdRestart: Permission given ({ctx.message.author}).")
        stream = os.popen("sudo systemctl restart " + service + " --no-pager -l --lines=3")
        output = stream.read()
        if output:
            await ctx.send(output)
        else:
            await ctx.send("No output.")
    else: 
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdAdd: Permission denied ({ctx.message.author}).")

@bot.command(hidden=True)
async def pStart(ctx, service):
    if ctx.message.author.id == auth.brady: 
        print(f"cmdStart: Permission given ({ctx.message.author}).")
        stream = os.popen("sudo systemctl start " + service + " --no-pager -l --lines=3")
        output = stream.read()
        if output:
            await ctx.send(output)
        else:
            await ctx.send("No output.")
    else: 
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdAdd: Permission denied ({ctx.message.author}).")

@bot.command(hidden=True)
async def pStop(ctx, service):
    if ctx.message.author.id == auth.brady: 
        print(f"cmdStop: Permission given ({ctx.message.author}).")
        stream = os.popen("sudo systemctl stop " + service + " --no-pager -l --lines=3")
        output = stream.read()
        if output:
            await ctx.send(output)
        else:
            await ctx.send("No output.")
    else: 
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdAdd: Permission denied ({ctx.message.author}).")

@bot.command(hidden=True)
async def pReboot(ctx):
    if ctx.message.author.id == auth.brady: 
        print(f"cmdReboot: Permission given ({ctx.message.author}).")
        await ctx.send("Are you sure? (y/n)")
        def check(m):
            return m.author == ctx.author
        try:
            msg = await bot.wait_for('message', check=check, timeout=5)
            if msg.content == "y" or msg.content == "Y":
                await ctx.send("Rebooting.")
                stream = os.popen("sudo reboot now")
            else:
                await ctx.send("Reboot canceled.")
        except asyncio.TimeoutError:
            await ctx.send("Reboot canceled (timeout).")
    else: 
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdAdd: Permission denied ({ctx.message.author}).")

bot.run(auth.TOKEN)