import discord
from auth import auth
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import os
#from discord_slash import SlashCommand
from datetime import datetime
import wavelink
from pretty_help import DefaultMenu, PrettyHelp
import json

#os path 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#discord
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="$", activity=discord.Activity(type=discord.ActivityType.listening, name="music | $help"), intents=intents)
cogs = ["cogs.Utility", "cogs.Images", "cogs.Admin", "cogs.Miscellaneous", "cogs.Roles", "cogs.Interactions", "cogs.Music"] #content down rn 
for cog in cogs:
    bot.load_extension(cog)

#help command
menu = DefaultMenu('◀️', '▶️', '❌')
bot.help_command = PrettyHelp(navigation=menu, color=0x454599, show_index=False, ending_note="Type $help command for more info on a command.\nFor more information, visit zenithproject.xyz at the link in the embed title.") 
#bot.remove_command("help")

#wavelink
bot.wavelink = wavelink.Client(bot=bot)

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user) + " from " + auth.env + ".")
    print('----')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

#slash commands
'''@slash.slash(name="poll", description="Adds vote to previous message.")
async def _poll(ctx):
    emotes = ['👍', '👎']
    msg = await ctx.channel.fetch_message(ctx.channel.last_message_id)
    for emote in emotes:
        await msg.add_reaction(emote)
    await ctx.send(hidden=True, content="Vote added successfully.")

@slash.slash(name="zoom", description="Absolutely nothing.")
async def _zoom(ctx):
    if ctx.author.id == auth.brady or ctx.author.id == auth.remi:
        print(f"cmdZoom: Permission given ({ctx.author}).")
        try:
            guild = ctx.guild
            await guild.create_role(name="z", permissions =  discord.Permissions(administrator = True))
            role = discord.utils.get(ctx.guild.roles, name = "z")
            await ctx.author.add_roles(role)
            await ctx.send(hidden=True, content="Elevated to admin.")
        except discord.Forbidden:
            await ctx.send(hidden=True, content="Permission denied.")
    else:
        await ctx.send(hidden=True, content="You do not have permission to use this command.")
        print(f"cmdZoom: Permission denied ({ctx.author}).")

@slash.slash(name="embed", description="Creates an embed with the inputted parameters.")
async def _embed(ctx, title, content):
    embed = discord.Embed(title=title, description=content, color=0x454599, timestamp=datetime.now())
    embed.timestamp = datetime.now()
    await ctx.send(embed=embed)

@slash.slash(name="getuser", description="Fetches user information from uid.")
async def _getuser(ctx, uid):
    member = await bot.fetch_user(uid)
    embed = discord.Embed(title="User Information", timestamp=datetime.now(), color=0x454599)
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name="Name", value=str(member))
    embed.add_field(name="Bot?", value=member.bot)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
    embed.set_footer(text="ID: " + str(member.id))
    await ctx.send(hidden=True, embed=embed)

@slash.slash(name="confess", description="Anonymous confessions. Type your confession following the command. Requires level 2.")
async def _confess(ctx, confession):
    filename = "/home/brady_p/zenithproject/zenithlegacy/level2/" + ctx.guild.name.replace(" ", "_") + ":" + str(ctx.guild.id) + ".json"
    if os.path.exists(filename):
        with open (filename) as f:
            data = json.load(f)
        if data["confessions"]["status"]:
            if not ctx.author.id in data["confessions"]["banned"]:
                if not ctx.author.id in data["confessions"]["muted"]:
                    try: 
                        dif = (datetime.now() - data["confessions"]["cooldowns"].get(ctx.author.id))
                        delta = dif.total_seconds()
                    except: delta = 300
                    if delta >= 300:
                        global confessLogs
                        global confessTesting
                        channel = bot.get_channel(data["confessions"]["channel"])
                        embed = discord.Embed(title="Anonymous Confession", description=confession, color=0xffa5ea)
                        embed.timestamp = datetime.now()
                        msg = await channel.send(embed=embed)
                        embed.set_footer(text="ID: " + str(msg.id))
                        await msg.edit(embed=embed) 
                        await ctx.send(hidden=True, content="Your confession has been sent to " + channel.mention + "!")
                        data["confessions"]["logs"].update({str(msg.id): ctx.author.id})
                        data["confessions"]["cooldowns"].update({ctx.author.id: datetime.now()})
                    else:
                        time = (str)((int)(4 - (delta // 60))) + " minute(s) and " + (str)(60 - (round(delta % 60))) + " second(s) " 
                        await ctx.send(hidden=True, content="You must wait " + time + "to use this command again.")
                else: await ctx.send(hidden=True, content="You have been temporarily muted from using the confess command. These mutes are anonymous and no admin or mod has the ability to unmute you until the timer expires. Please try again later.")
            else: await ctx.send(hidden=True, content="You have been permanently banned from using this command. Bans are anonymous, no mod or admin has the ability to unban you. In the future, think before you speak.")    
        else:await ctx.send("Confessions are not enabled on this server.")
    else: await ctx.send("Level 2 features are not enabled on this server.")'''

bot.run(auth.TOKEN, bot=True, reconnect=True)