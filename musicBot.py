from asyncio.queues import QueueEmpty
import discord
import auth
import wavelink
from discord.ext import commands
import asyncio
from random import shuffle as pyShuffle

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
    async def disconnect(self):
        await self.player.disconnect()

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

    #plays queue
    async def play(self, ctx):
        while True:
            try:
                track = self.queue.get_nowait()
                await ctx.send(f'Now playing: {track}.')
                await self.player.play(track)
                self.playing = track
                while self.player.is_playing:
                    await asyncio.sleep(1)
            except QueueEmpty:
                await self.player.stop()
                break

    #prints currently playing song
    async def nowPlaying(self, ctx):
        await ctx.send(self.playing)
        
    #skips current song
    async def skip(self):
        await self.player.stop()

    #delete queue
    async def clearQueue(self):
        stop = object()
        await self.queue.put(stop)
        track = self.queue.get_nowait()
        while track is not stop:
            track = self.queue.get_nowait()

    #pauses player
    async def pause(self):
        await self.player.set_pause(True)

    #resumes player
    async def resume(self):
        await self.player.set_pause(False)
        
    #shuffles queue
    async def shuffleQueue(self):
        pyShuffle(self.queue._queue)

#bot
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="$help"))
    await bot.wavelink.initiate_node(host=auth.lavaIp, port=auth.lavaPort, rest_uri=auth.lavaAddr, password=auth.lavaPw, identifier='MAIN', region='us_east')
    global playerMap
    playerMap = {}
    for guild in bot.guilds:
        playerMap[guild.id] = Player(guild)
    print('Logged in as {0} ({0.id})'.format(bot.user) + " from " + auth.env + ".")
    print('----')

@bot.command(hidden=True, brief="Returns bot state")
async def info(ctx):
    print(f"cmdInfo: Permission given ({ctx.message.author}).")
    await ctx.send('Music logged in as {0} ({0.id})'.format(bot.user) + " from " + auth.env + ".")

@bot.command(brief="Connects bot to voice", description="Connects bot to whatever voice channel the user is in.", aliases=["connect"])
async def hi(ctx):
    player = playerMap[ctx.guild.id]
    await player.connect(ctx)

@bot.command(brief="Disconnects bot from voice", description="Disconnects bot from voice.", aliases=["disconnect"])
async def die(ctx):
    player = playerMap[ctx.guild.id]
    await player.clearQueue()
    await player.disconnect()
    await ctx.send("Disconnected.")

@bot.command(brief="Plays specified song", description="Plays specified song.", aliases=["play"])
async def p(ctx, *args):
    input = ' '.join(args[:])
    player = playerMap[ctx.guild.id]
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

@bot.command(brief="Displays the queue", description="Displays the queue.", aliases=["queue"])
async def q(ctx):
    player = playerMap[ctx.guild.id]
    await player.getQueue(ctx)

@bot.command(brief="Displays currently playing song", description="Displays currently playing song.", aliases=["playing"])
async def np(ctx):
    player = playerMap[ctx.guild.id]
    await player.nowPlaying(ctx)

@bot.command(brief="Skips currently playing song", description="Skips currently playing song.", aliases=["skip"])
async def s(ctx):
    player = playerMap[ctx.guild.id]
    await player.skip()
    await ctx.send("Track skipped.")

@bot.command(brief="Shuffles queue", description="Shuffles queue.")
async def shuffle(ctx):
    player = playerMap[ctx.guild.id]
    await player.shuffleQueue()
    await ctx.send("Queue has been shuffled.")

@bot.command(brief="Clears queue", description="Clears queue.")
async def clear(ctx):
    player = playerMap[ctx.guild.id]
    await player.clearQueue()
    await ctx.send("Queue cleared.")

@bot.command(brief="Pauses player", description="Pauses player.")
async def pause(ctx):
    player = playerMap[ctx.guild.id]
    if player.player.is_paused:
        await ctx.send("This player is already paused.")
    else:
        await player.pause()
        await ctx.send("Player paused.")

@bot.command(brief="Resumes paused player", description="Resumes paused player.")
async def resume(ctx):
    player = playerMap[ctx.guild.id]
    if not player.player.is_paused:
        await ctx.send("This player is already playing.")
    else:
        await player.resume()
        await ctx.send("Player resumed.")

bot.run(auth.TOKEN)