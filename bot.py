from types import ClassMethodDescriptorType
import discord
import auth
from discord.ext import commands
from discord.utils import get
import asyncio
import wolframalpha
import wikipedia
import re
from google.cloud import translate_v2 as translate
import resources
from discord import Member
import random
import os
from discord.ext.commands import CommandNotFound
from PIL import Image, ImageOps, ImageFilter
import requests
from io import BytesIO
from discord_slash import SlashCommand, SlashContext
import cryptography
from cryptography.fernet import Fernet
import json
from datetime import datetime
import binascii
import struct
import numpy as np
import scipy
import scipy.misc
import scipy.cluster
from colorthief import ColorThief

#os path 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#wolfram alpha
wclient = wolframalpha.Client(auth.appId)

#googletranslate
translate_client = translate.Client.from_service_account_json("DiscordBot-b0d16fb53e59.json")

#discord
bot = commands.Bot(command_prefix="$")
slash = SlashCommand(bot, sync_commands=True)

#help command
HelpCommand = commands.DefaultHelpCommand(no_category = "General Commands")
bot.help_command = HelpCommand

#encryption
#key = Fernet.generate_key()
#with open('confessions.key', 'wb') as f:
    #f.write(key)
with open('confessions.key', 'rb') as f:
    key = f.read()
fernet = Fernet(key)
global confessBanned
confessBanned = []

global confessLogs
confessLogs = {}
global confessCooldowns
confessCooldowns = {}
global confessMuted
confessMuted = []
global confessToggle
confessToggle = True
global confessTesting
confessTesting = False

def encrypt(fileName):
    fernet = Fernet(key)
    with open (fileName, 'rb') as f:
        encrypted = fernet.encrypt(f.read())
    with open (fileName, 'wb') as f:
        f.write(encrypted)

def decrypt(fileName):
    fernet = Fernet(key)
    with open (fileName, 'rb') as f:
        decrypted = fernet.decrypt(f.read())
    with open (fileName, 'wb') as f:
        f.write(decrypted)
        
try:    
    with open ('confessBanned.json') as f:
        confessBanned = json.load(f)
    encrypt('confessBanned.json')
except: 
    try: 
        decrypt('confessBanned.json')
        with open ('confessBanned.json') as f:
            confessBanned = json.load(f)
        encrypt('confessBanned.json')
    except: pass

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user) + " from " + auth.env + ".")
    print('----')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="music | $help"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

@bot.command(brief="Returns bot state", description="Returns bot state.")
async def info(ctx):
    print(f"cmdInfo: Permission given ({ctx.message.author}).")
    await ctx.send('Release logged in as {0} ({0.id})'.format(bot.user) + " from " + auth.env + ".")

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

@bot.command(brief="Changes mentioned user's nickname", description="Changes mentioned user's nickname.")
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

@bot.command(brief="Mutes mentioned user in text channels", description="Mutes mentioned user in text channels.")
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

@bot.command(brief="Unmutes previously muted user", description="Unmutes previously muted user.")
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
    async with ctx.channel.typing():
        input = ' '.join(args[:])
        print(f'cmdAsk: Search query "{input}"')
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

@bot.command(brief="Returns a Wikipedia page for the given term", description="Returns a Wikipedia page for the given term.")
async def wiki(ctx, *args):
    async with ctx.channel.typing():
        input = ' '.join(args[:])
        print(f'cmdWiki: Search query "{input}"')
        res = wikipedia.search(input)
        if not res:
            print(f'cmdWiki: No result from wikipedia.')
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

@bot.command(brief="Translates given text into given language", description="Translates given text into given language. See syntax below. Command autodetects source language.")
async def translate(ctx, langInput, *input):
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
            print(f'cmdTranslate: Translation error. Input = "{content}"')
        await ctx.send(embed=embed)

@bot.command(brief="Returns image of the specified user's profile picture", description="Returns image of the specified user's profile picture. Defaults to message sender.")
async def pfp(ctx, *args):
    print(f"cmdPfp: Permission given ({ctx.message.author}).")
    if len(ctx.message.mentions) > 0:
        member = ctx.message.mentions[0]
    else:
        member = ctx.message.author
    if args:
        res = requests.get(member.avatar_url, size=512)
        image = Image.open(BytesIO(res.content)).convert('RGB')
            
        for i in args:
            if i == "inv" or i == "invert" or i == "ivt":
                image = ImageOps.invert(image)
            elif i == "blur":
                image = image.filter(ImageFilter.BLUR)
            elif i == "contour":
                image = image.filter(ImageFilter.CONTOUR)
            elif i == "emboss":
                image = image.filter(ImageFilter.EMBOSS)
            elif i == "edges":
                image = image.filter(ImageFilter.FIND_EDGES)
            elif i == "communism":
                filter = Image.open(r"./images/communism.jpg")
                image.paste(filter, (0, 0))
                    
        with BytesIO() as imageBinary:
            image.save(imageBinary, 'PNG')
            imageBinary.seek(0)
            await ctx.send(file=discord.File(fp=imageBinary, filename='image.png'))
    else: 
        await sendAsEmbed(ctx, member)

async def sendAsEmbed(ctx, member):
    embed = discord.Embed()
    embed.set_image(url=member.avatar_url_as(size=512))
    await ctx.send(embed=embed)

@bot.command(brief="Delete a chosen number of messages", description="Delete a chosen number of messages. Command usable by those with manage messages permission.")
async def purge(ctx, num):
    clear = int(num) + 1
    if ctx.message.author.guild_permissions.manage_messages:
        print(f"cmdPurge: Permission given ({ctx.message.author}). Messages cleared = " + str(clear) + ".")
        await ctx.channel.purge(limit=clear)
    else: 
        print(f"cmdPurge: Permission denied ({ctx.message.author}).")
        await ctx.send("You do not have permission to use this command.")

@bot.command(brief="Creates an invite to this server", description="Creates an invite to this server.")
async def invite(ctx):
    link = await ctx.channel.create_invite(max_age = 0)
    await ctx.send(link)

@bot.command(brief="Kicks mentioned user after a specified amount of time", description="Kicks mentioned user after a specific amount of time (hours).")
async def timekick(ctx, member:discord.Member, time, unit):
    if ctx.message.author.guild_permissions.kick_members:
        if str(unit) == "minute" or str(unit) == "minutes" or str(unit) == "min" or str(unit) == "mins":
            time = round(float(time) / 60, 2)
        print(f"cmdExpire: Permission given ({ctx.message.author}). Time = {time} hour(s). Member = {member.display_name}.")
        await kickTimer(ctx, member, time)
    else:
        await ctx.send("You do not have permission to use this command.")

async def kickTimer(ctx, member:discord.Member, time):
    print("kickTimer called.")
    await ctx.send(f"Member {member.display_name} will be kicked after {time} hour(s).")
    time = time * 3600
    await asyncio.sleep(time)
    try:
        await member.kick()
        print(f"Member {member.display_name} was kicked after timer expire.")
        await ctx.send(f"Member {member.display_name} was kicked after timer expire.")
    except discord.Forbidden:
        print("Member kick failed after timer expire.")

@bot.command(brief="Kicks mentioned user after they leave vc", description="Kicks mentioned user after they leave vc.")
async def vckick(ctx, member:discord.Member):
    if ctx.message.author.guild_permissions.kick_members:
        print(f"cmdVckick: Permission given ({ctx.message.author}). Member = {member.display_name}.")
        if member.voice == None:
            await ctx.send(f"Member {member.display_name} is not in a vc.")
        else:
            await ctx.send(f"Member {member.display_name} will be kicked after they leave vc.")
            await vcKicker(ctx, member)
            
    else:
        await ctx.send("You do not have permission to use this command.")

async def vcKicker(ctx, member:discord.Member):
    while True:
        if member.voice == None:
            await member.kick()
            break
        else:
            await asyncio.sleep(60)
    await ctx.send(f"Member {member.display_name} was kicked after leaving vc.")
    
@bot.command(brief="Sends a pickup line", description="Sends a pickup line.")
async def pickup(ctx, member:discord.Member):
    print("cmdPickup")
    line = random.choice(resources.pickupLines).replace("{name}", member.mention).replace("{author}", ctx.author.mention)
    await ctx.send(line)

@bot.command(brief="Flips a coin", description="Flips a coin.")
async def coinflip(ctx):
    print("cmdCoinflip")
    res = random.choice(["Heads.", "Tails."])
    await ctx.send(res)

@bot.command(brief="Picks a random choice from a list of inputs separated by commas", description="Picks a random choice from a list of inputs separated by commas.")
async def randomchoice(ctx, *args):
    print("cmdRandomchoice")
    choices = ' '.join(args[:]).split(',')
    res = random.choice(choices)
    await ctx.send(res)

@bot.command(brief="Returns schedule for specified school (hhs, slhs)", description="Returns schedule for specified school (hhs, slhs).")
async def bell(ctx, school, *args):
    print("cmdBell")
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

@bot.command(hidden=True)
async def confessmute(ctx, id, time, unit):
    if ctx.author.guild_permissions.mute_members:
        print(f"cmdConfessmute: Permission given ({ctx.author}).")
        global confessLogs
        global confessMuted
        if id.startswith("https"):
            id = str(id.rsplit('/', 1)[-1])
        if str(unit) == "minute" or str(unit) == "minutes" or str(unit) == "min" or str(unit) == "mins":
            time = round(float(time) / 60, 2)
        confessMuted.append(confessLogs.get(id))
        await ctx.send(f"Author of message ID \"{id}\" has been anonymously muted for {time} hour(s).")
        await confessMuteTimer(id, time)
    else:
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdConfessmute: Permission denied ({ctx.author}).")

async def confessMuteTimer(id, time):
    global confessLogs
    global confessMuted
    time = time * 3600
    await asyncio.sleep(time)
    confessMuted.remove(confessLogs.get(id))

@bot.command(hidden=True)
async def confessban(ctx, id):
    if ctx.author.guild_permissions.mute_members:
        print(f"cmdConfessmute: Permission given ({ctx.author}).")
        fernet = Fernet(key)
        global confessLogs
        global confessBanned
        if id.startswith("https"):
            id = str(id.rsplit('/', 1)[-1])
        try:    
            with open ('confessBanned.json') as f:
                confessBanned = json.load(f)
        except: 
            try: 
                decrypt('confessBanned.json')
                with open ('confessBanned.json') as f:
                    confessBanned = json.load(f)
            except: pass
        if id in confessLogs:
            if not confessLogs.get(id) in confessBanned: confessBanned.append(confessLogs.get(id))
            await ctx.send(f"Author of message ID \"{id}\" has been permanently banned from use of the confess command.")
        else: 
            await ctx.send("Message id could not be found. Please try again.")
        with open ('confessBanned.json', 'w') as f:
            json.dump(confessBanned, f)
        encrypt('confessBanned.json')
    else:
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdConfessmute: Permission denied ({ctx.author}).")

@bot.command(hidden=True)
async def confesstesting(ctx):
    if ctx.author.id == auth.brady:
        global confessTesting
        if confessTesting == False:
            confessTesting = True
            await ctx.send("Testing mode set to true.")
        else:
            confessTesting = False
            await ctx.send("Testing mode set to false.")
    else:
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdConfesstesting: Permission denied ({ctx.author}).")

@bot.command(hidden=True)
async def confesstoggle(ctx):
    if ctx.author.guild_permissions.mute_members:
        print(f"cmdConfesstoggle: Permission given ({ctx.author}).")
        global confessToggle
        if confessToggle == False:
            confessToggle = True
            await ctx.send("Confessions enabled.")
        else:
            confessToggle = False
            await ctx.send("Confessions disabled.")
    else:
        await ctx.send("You do not have permission to use this command.")
        print(f"cmdConfesstoggle: Permission denied ({ctx.author}).")

@slash.slash(name="confess",guild_ids=[auth.mmr],description="Anonymous confessions. Type your confession following the command.")
async def _confess(ctx, *confession):
    if confessToggle == True:
        global confessBanned
        if not ctx.author.id in confessBanned:
            global confessMuted
            if not ctx.author.id in confessMuted:
                global confessCooldowns
                try: 
                    dif = (datetime.now() - confessCooldowns.get(ctx.author.id))
                    delta = dif.total_seconds()
                except: delta = 300
                if delta >= 300:
                    global confessLogs
                    global confessTesting
                    input = ' '.join(confession[:])
                    if confessTesting == True:
                        channel = bot.get_channel(700802727764295771)
                    else:
                        channel = bot.get_channel(835149061576589362)
                    embed = discord.Embed(title="Anonymous Confession",description=input,color=0xffa5ea)
                    embed.timestamp = datetime.now()
                    msg = await channel.send(embed=embed)
                    embed.set_footer(text="ID: " + str(msg.id))
                    await msg.edit(embed=embed) 
                    await ctx.send(hidden=True, content="Your confession has been sent to " + channel.mention + "!")
                    confessLogs.update({str(msg.id): ctx.author.id})
                    confessCooldowns.update({ctx.author.id: datetime.now()})
                else:
                    time = (str)((int)(4 - (delta // 60))) + " minute(s) and " + (str)(60 - (round(delta % 60))) + " second(s) " 
                    await ctx.send(hidden=True, content="You must wait " + time + "to use this command again.")
            else: await ctx.send(hidden=True, content="You have been temporarily muted from using the confess command. These mutes are anonymous and no admin or mod has the ability to unmute you until the timer expires. Please try again later.")
        else: await ctx.send(hidden=True, content="You have been permanently banned from using this command. Bans are anonymous, no mod or admin has the ability to unban you. In the future, think before you speak.")    
    else: await ctx.send(hidden=True, content="Confessions have been disabled on this server. Message a mod or an admin if you think this is a mistake. Please try again later.")

@bot.command(brief="Returns preview of colors", description="Returns preview of colors.", aliases=["c"])
async def color(ctx, *args):
    images = []
    stops = []
    for i in args:
        hex = i.lstrip('#')
        rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
        image = Image.new('RGB', (50, 50), rgb)
        images.append(image)
    for i in range(100, 0, -1):
        if len(images) >= i ** 2 and len(images) % i == 0:
            height = i * 50
            width = int(len(images) / i) * 50
            for j in range(1, i):
                stops.append(int(len(images) / i * j))
            break
    
    #print(str(width) + " , " + str(height))
    output = Image.new('RGB', (width, height))
    xOffset = 0
    yOffset = 0
    index = 0
    for image in images:
        for stop in stops:
            if index == stop:
                yOffset += 50
                xOffset = 0
        #print(str(xOffset) + " , " + str(yOffset))
        output.paste(image, (xOffset, yOffset))
        xOffset += image.size[0]
        index += 1
    with BytesIO() as imageBinary:
        output.save(imageBinary, 'PNG')
        imageBinary.seek(0)
        await ctx.send(file=discord.File(fp=imageBinary, filename='image.png'))

#alpha
@bot.command(brief="Returns a collage of the inputted pictures", description="Returns a collage of the inputted pictures")
async def collage(ctx):
    images = []
    stops = []
    for i in ctx.message.attachments:
        res = requests.get(i.url)
        image = Image.open(BytesIO(res.content)).convert('RGB')
        images.append(image)
    for i in range(100, 0, -1):
        if len(images) >= i ** 2 and len(images) % i == 0:
            height = i * 50
            width = int(len(images) / i) * 50
            for j in range(1, i):
                stops.append(int(len(images) / i * j))
            break
    #print(str(width) + " , " + str(height))
    output = Image.new('RGB', (width, height))
    xOffset = 0
    yOffset = 0
    index = 0
    for image in images:
        for stop in stops:
            if index == stop:
                yOffset += 50
                xOffset = 0
        #print(str(xOffset) + " , " + str(yOffset))
        output.paste(image, (xOffset, yOffset))
        xOffset += image.size[0]
        index += 1
    with BytesIO() as imageBinary:
        output.save(imageBinary, 'PNG')
        imageBinary.seek(0)
        await ctx.send(file=discord.File(fp=imageBinary, filename='image.png'))

@bot.command(hidden=True, brief="Returns the most used colors in an image", description="Returns the most used colors in an image.")
async def pal2(ctx):
    clusters = 5
    res = requests.get(ctx.message.attachments[0].url)
    image = Image.open(BytesIO(res.content)).convert('RGB')
    image = image.resize((256, 256))
    array = np.asarray(image)
    shape = array.shape
    array = array.reshape(np.product(shape[:2]), shape[2]).astype(float)
    codes, dist = scipy.cluster.vq.kmeans(array, clusters)
    vecs, dist = scipy.cluster.vq.vq(array, codes)        
    counts, bins = np.histogram(vecs, len(codes))    
    max = np.argmax(counts)                    
    peak = codes[max]
    hex = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')
    await ctx.send("#" + hex)
    rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    output = Image.new('RGB', (50, 50), rgb)
    with BytesIO() as imageBinary:
        output.save(imageBinary, 'PNG')
        imageBinary.seek(0)
        await ctx.send(file=discord.File(fp=imageBinary, filename='image.png'))

@bot.command(brief="Returns the most used colors in an image", description="Returns the most used colors in an image.", aliases=["pal"])
async def palette(ctx, num):
    images = []
    stops = []
    res = requests.get(ctx.message.attachments[0].url)
    image = Image.open(BytesIO(res.content)).convert('RGB')
    cthief = ColorThief(BytesIO(res.content))
    if int(num) == 1:
        rgb = cthief.get_color(quality=1)
        image = Image.new('RGB', (50, 50), rgb)
        images.append(image)
    elif int(num) == 2:
        for i in range(1, 3):
            rgb = cthief.get_color(quality=2)
            image = Image.new('RGB', (50, 50), rgb)
            images.append(image)
    else:
        palette = cthief.get_palette(color_count=int(num) - 1)
        for rgb in palette:
            image = Image.new('RGB', (50, 50), rgb)
            images.append(image)
    for i in range(100, 0, -1):
        if len(images) >= i ** 2 and len(images) % i == 0:
            height = i * 50
            width = int(len(images) / i) * 50
            for j in range(1, i):
                stops.append(int(len(images) / i * j))
            break
    #print(str(width) + " , " + str(height))
    output = Image.new('RGB', (width, height))
    xOffset = 0
    yOffset = 0
    index = 0
    for image in images:
        for stop in stops:
            if index == stop:
                yOffset += 50
                xOffset = 0
        #print(str(xOffset) + " , " + str(yOffset))
        output.paste(image, (xOffset, yOffset))
        xOffset += image.size[0]
        index += 1
    with BytesIO() as imageBinary:
        output.save(imageBinary, 'PNG')
        imageBinary.seek(0)
        await ctx.send(file=discord.File(fp=imageBinary, filename='image.png'))

bot.run(auth.TOKEN)