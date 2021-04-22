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

#help command
HelpCommand = commands.DefaultHelpCommand(
    no_category = "Commands"
)
bot.help_command = HelpCommand

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

@bot.command(hidden=True, brief="Returns bot state")
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
        #await ctx.send(member)
        #args2 = args[1:]
        #await ctx.send(args2)
    else:
        member = ctx.message.author  
        #await ctx.send(member)      
        #await ctx.send(args)
    try:
        if args[0] == "inv" or args[0] == "invert":
            res = requests.get(member.avatar_url)
            image = Image.open(BytesIO(res.content)).convert('RGB')
            out = ImageOps.invert(image)
            with BytesIO() as imageBinary:
                out.save(imageBinary, 'PNG')
                imageBinary.seek(0)
                await ctx.send(file=discord.File(fp=imageBinary, filename='image.png'))
    except:
        await ctx.send(member.avatar_url_as(size=512))

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

bot.run(auth.TOKEN)
