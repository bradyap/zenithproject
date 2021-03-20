from asyncio.queues import QueueEmpty
import discord
import auth
import wavelink
from discord.ext import commands
import asyncio

#discord
bot = commands.Bot(command_prefix="$")
bot.remove_command('help')

#wavelink
bot.wavelink = wavelink.Client(bot=bot)

class Player:
    def __init__(self, guild):
        self.gId = guild.id
        self.player = bot.wavelink.get_player(self.gId)
        self.queue = asyncio.Queue()
        self.loop = asyncio.get_event_loop
        self.playing = "No song is currently playing."

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
        await self.player.destroy()
        await ctx.send("Disconnected.")

    #prints queue
    async def getQueue(self, ctx):
        embed = discord.Embed(title="Music Queue")
        stop = object()
        track = object()
        await self.queue.put(stop)
        track = self.queue.get_nowait()
        while track is not stop:
            embed.add_field(name='\u200b', inline=False, value=track)
            await self.queue.put(track)
            track = self.queue.get_nowait()
        await ctx.send(embed=embed)

    #adds to queue
    async def add(self, ctx, track):
        await self.player.queue.put(track)
        await ctx.send(f'Added {track} to the queue.')

    #plays queue
    async def play(self, ctx):
        while True:
            try:
                track = self.queue.get_nowait()
                await ctx.send(f'Now playing: {track}.')
                await self.player.play(track)
                self.playing = track
                #length of track in seconds (+1 for overhead)
                length = (track.length / 1000) + 1
                await asyncio.sleep(length)
            except QueueEmpty:
                break
        
    #prints currently playing song
    async def nowPlaying(self, ctx):
        await ctx.send(self.playing)
    
#skips current track
async def skip(ctx, oldPlayer):
    stop = object()
    track = object()
    temp = asyncio.Queue()
    #copy player queue to temp
    await oldPlayer.queue.put(stop)
    track = oldPlayer.queue.get_nowait()
    while track is not stop:
        await temp.put(track)
        track = oldPlayer.queue.get_nowait()
    #destroy original player and makes new one
    await oldPlayer.player.destroy()
    queueMap[ctx.guild.id] = Player(ctx.guild)
    player = queueMap[ctx.guild.id]
    #copy temp into new player
    await temp.put(stop)
    track = temp.get_nowait()
    while track is not stop:
        await player.queue.put(track)
        track = temp.get_nowait()
    await ctx.send("Track skipped.")

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
    del player
    queueMap[ctx.guild.id] = Player(ctx.guild)

@bot.command(brief="Plays specified song", description="Plays specified song.")
async def p(ctx, *args):
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
async def q(ctx):
    player = queueMap[ctx.guild.id]
    await player.getQueue(ctx)
    
@bot.command(brief="Displays currently playing song", description="Displays currently playing song.")
async def np(ctx):
    player = queueMap[ctx.guild.id]
    await player.nowPlaying(ctx)

@bot.command(brief="Skips currently playing song", description="Skips currently playing song.")
async def s(ctx):
    oldPlayer = queueMap[ctx.guild.id]
    await skip(ctx, oldPlayer)

bot.run(auth.TOKEN)