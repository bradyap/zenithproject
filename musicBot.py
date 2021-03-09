from asyncio.queues import QueueEmpty
import discord
import auth
import wavelink
from discord.ext import commands
import asyncio

#discord
bot = commands.Bot(command_prefix="$")
HelpCommand = commands.DefaultHelpCommand(
    no_category = "Music Commands"
)
bot.help_command = HelpCommand

#wavelink
bot.wavelink = wavelink.Client(bot=bot)

def make_sleep():
    async def sleep(delay, result=None, *, loop=None):
        coro = asyncio.sleep(delay, result=result, loop=loop)
        task = asyncio.ensure_future(coro)
        sleep.tasks.add(task)
        try:
            return await task
        except asyncio.CancelledError:
            return result
        finally:
            sleep.tasks.remove(task)

    sleep.tasks = set()
    sleep.cancel_all = lambda: sum(task.cancel() for task in sleep.tasks)
    return sleep

class Player:
    def __init__(self, guild):
        self.gId = guild.id
        self.player = bot.wavelink.get_player(self.gId)
        self.queue = asyncio.Queue()
        self.loop = asyncio.get_event_loop

    #connect
    async def connect(self, ctx):
        if not self.player.is_connected:
            try:
                channel = ctx.author.voice.channel
                await ctx.send(f"Connecting to {channel.name}.")
                await self.player.connect(channel.id)
            except AttributeError:
                await ctx.send("Please join a voice channel.")

    #disconnect
    async def disconnect(self, ctx):
        make_sleep.cancelAll()
        await self.player.destroy()
        await ctx.send("Disconnected.")

    #prints queue
    async def getQueue(self, ctx):
        await ctx.send(self.queue)

    #next song in queue
    async def nextSong(self):
        while True:
            await self.queue.get()

    #adds to queue
    async def add(self, ctx, track):
        await self.player.queue.put(track)
        await ctx.send(f'Added {track} to the queue.')

    #plays queue
    async def play(self, ctx):
        while True:
            try:
                track = self.queue.get_nowait()
                await ctx.send(f'Now playing: {track.title}.')
                await self.player.play(track)
                #length of track in seconds (+1 for overhead)
                length = (track.length / 1000) + 1
                await sleep(length)
                #await self.sleeper.sleep(length)
            except QueueEmpty:
                break
    
#bot
@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user) + ".")
    print('----')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="$help"))
    await bot.wavelink.initiate_node(host=auth.lavaIp, port=auth.lavaPort, rest_uri=auth.lavaAddr, password=auth.lavaPw, identifier='MAIN', region='us_east')
    global queueMap, sleeperMap
    queueMap = {}
    sleeperMap = {}
    for guild in bot.guilds:
        queueMap[guild.id] = Player(guild)

@bot.command(hidden=True, brief="Returns bot state")
async def info(ctx):
    print(f"cmdInfo: Permission given ({ctx.message.author}).")
    await ctx.send('Music - logged in as {0} ({0.id})'.format(bot.user))
    
@bot.command(brief="Connects bot to voice", description="Connects bot to whatever voice channel the user is in.")
async def hi(ctx):
    player = queueMap[ctx.guild.id]
    await player.connect(ctx)

@bot.command(brief="Disconnects bot from voice", description="Disconnects bot from voice.")
async def die(ctx):
    player = queueMap[ctx.guild.id]
    await player.disconnect(ctx)

@bot.command(brief="Plays specified song", description="Plays specified song.")
async def play(ctx, *args):
    input = ' '.join(args[:])
    player = queueMap[ctx.guild.id]
    print(f'cmdPlay: Search query "{input}"')
    res = await bot.wavelink.get_tracks(f'ytsearch:{input}')
    if not res:
        await ctx.send('Could not find any songs with that query.')
    else:
        #adds track to queue
        await player.queue.put(res[0])
        await ctx.send(f'Added {str(res[0])} to the queue.')
        await player.connect(ctx)
        if not player.player.is_playing:
            await player.play(ctx)

@bot.command(brief="Displays the queue", description="Displays the queue.")
async def queue(ctx):
    player = queueMap[ctx.guild.id]
    await player.getQueue(ctx)

bot.run(auth.TOKEN)