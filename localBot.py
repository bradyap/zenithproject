import os
import discord
import auth
from discord.errors import HTTPException
from discord.ext import commands
import subprocess
from discord.ext.commands import CommandNotFound

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
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="$help"))

@bot.command(hidden=True, brief="Returns bot state")
async def info(ctx):
    print(f"cmdInfo: Permission given ({ctx.message.author}).")
    await ctx.send('Local logged in as {0} ({0.id})'.format(bot.user) + " from " + auth.env + ".")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

@bot.command(hidden=True)
async def launch(ctx, item):
    if ctx.message.author.id == auth.brady or ctx.message.author.id == 485794062448852993 or ctx.message.author.id ==558430263013670922:
        print(f"cmdLaunch: Permission given ({ctx.message.author}). Item = {item}")
        if item == "val":
            process = subprocess.Popen(["C:\Riot Games\Riot Client\RiotClientServices.exe", "--launch-product=valorant", "--launch-patchline=live"])
            await ctx.send("Attempting to launch Valorant.")   
    else:
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdLaunch: Permission denied ({ctx.message.author}).")

@bot.command(hidden=True)
async def join(ctx, *args):
    subject = " ".join(args[:])
    if ctx.message.author.id == auth.brady:
        print(f"cmdSubject: Permission given ({ctx.message.author}). Subject = {subject}.")
        if subject == "spanish":
            os.system("start chrome " + auth.spanish)
            await ctx.send(f"Joining {subject}.")
        elif subject == "anatomy":
            os.system("start chrome " + auth.anatomy)
            await ctx.send(f"Joining {subject}.")
        elif subject == "english":
            os.system("start chrome " + auth.english)
            await ctx.send(f"Joining {subject}.")
        elif subject == "english stinger":
            os.system("start chrome " + auth.englishStinger)
            await ctx.send(f"Joining {subject}.")
        elif subject == "precalc":
            os.system("start chrome " + auth.precalc)
            await ctx.send(f"Joining {subject}.")
        elif subject == "comp sci":
            os.system("start chrome " + auth.compSci)
            await ctx.send(f"Joining {subject}.")
        elif subject == "apush":
            os.system("start chrome " + auth.apush)
            await ctx.send(f"Joining {subject}.")
        elif subject == "cybersecurity":
            os.system("start chrome " + auth.cybersecurity)
            await ctx.send(f"Joining {subject}.")
        else:
            await ctx.send(f"Joining {subject}.")
    else:
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdAdd: Permission denied ({ctx.message.author}). Subject = {subject}.")

@bot.command(hidden=True)
async def cmd(ctx, *args):
    input = " ".join(args[:])
    if ctx.message.author.id == auth.brady: 
        print(f"cmdCmd: Permission given ({ctx.message.author}). Input = {input}.")
        stream = os.popen(input)
        output = stream.read()
        try:
            await ctx.send(output)
        except HTTPException:
            await ctx.send("No output. Check command and try again.")
    else: 
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdAdd: Permission denied ({ctx.message.author}). Input = {input}.")

bot.run(auth.TOKEN)