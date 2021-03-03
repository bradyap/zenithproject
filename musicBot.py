import discord
import auth
import wavelink
from discord.ext import commands

#discord
bot = commands.Bot(command_prefix="$")
HelpCommand = commands.DefaultHelpCommand(
    no_category = "Music Commands"
)
bot.help_command = HelpCommand

#wavelink
bot = bot
bot.wavelink = wavelink.Client(bot=bot)

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user) + ".")
    print('----')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="$help"))
    await bot.wavelink.initiate_node(host=auth.lavaIp, port=auth.lavaPort, rest_uri=auth.lavaAddr, password=auth.lavaPw, identifier='MAIN', region='us_east')

@bot.command(hidden=True, brief="Returns bot state")
async def info(ctx):
    print(f"cmdInfo: Permission given ({ctx.message.author}).")
    await ctx.send('Music - logged in as {0} ({0.id})'.format(bot.user))
    
@bot.command(brief="Connects bot to voice.", description="Connects bot to whatever voice channel the user is in.")
async def hi(ctx):
    try:
        channel = ctx.author.voice.channel
        player = bot.wavelink.get_player(ctx.guild.id)
        await ctx.send(f"Connecting to {channel.name}")
        await player.connect(channel.id)
    except AttributeError:
        await ctx.send("Please join a voice channel.")

@bot.command(brief="Disconnects bot from voice.", description="Disconnects bot from voice.")
async def die(ctx):
    player = bot.wavelink.get_player(ctx.guild.id)
    await player.destroy()
    await ctx.send("Disconnected.") 

@bot.command(brief="Plays specified song.", description="Plays specified song.")
async def play(ctx, *args):
    input = ' '.join(args[:])
    print(f'cmdPlay: Search query "{input}"')
    res = await bot.wavelink.get_tracks(f'ytsearch:{input}')
    if not res:
        return await ctx.send('Could not find any songs with that query.')

    player = bot.wavelink.get_player(ctx.guild.id)

    await ctx.send(f'Added {str(res[0])} to the queue.')
    await player.play(res[0])

bot.run(auth.TOKEN)