from asyncio.queues import QueueEmpty
import discord
import auth
import wavelink
from discord.ext import commands
import asyncio
from random import shuffle as pyShuffle
import os
from discord.ext.commands import CommandNotFound
import requests
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#os path 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#discord
bot = commands.Bot(command_prefix="$")

#help command
HelpCommand = commands.DefaultHelpCommand(
    no_category = "Music Commands"
)
bot.help_command = HelpCommand

#wavelink
bot.wavelink = wavelink.Client(bot=bot)

#url regex
urlReg = re.compile(r'https?://(?:www\.)?.+')

#spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=auth.spotifyId, client_secret=auth.spotifySecret))

class Player:
    def __init__(self, guild):
        self.gId = guild.id
        self.player = bot.wavelink.get_player(self.gId)
        #self.queue = asyncio.Queue()
        self.queue = []
        self.index = 0
        self.loopStatus = 0
        self.playing = "No song is currently playing."

    #connect
    async def connect(self, ctx):
        if not self.player.is_connected:
            try:
                channel = ctx.author.voice.channel
                await ctx.send(f"`Connecting to {channel.name}.`")
                await self.player.connect(channel.id)
            except AttributeError:
                await ctx.send("`Please join a voice channel.`")

    #disconnect
    async def disconnect(self):
        await self.player.disconnect()
        await self.player.stop()
        self.loopStatus = 0

    #prints queue
    async def getQueue(self, ctx):
        out = "```yaml\nQueue:"
        for i in range(len(self.queue)):
            if self.queue[i] == self.playing: out += "\n- - - NOW PLAYING - - -" + "\n#" + str(i + 1) + ") " + self.queue[i].title + "\n- - - NOW PLAYING - - -"
            else: out += "\n" + str(i + 1) + ") " + self.queue[i].title
        await ctx.send(out + "```")

    #plays queue
    async def play(self, ctx):
        while True:
            track = self.queue[self.index]
            #embed = discord.Embed(title="Now Playing", description=track)
            #embed = discord.Embed(title="Now Playing", url=track.uri, description=track)
            #try:
                #embed.set_thumbnail(url=track.thumb)
            #except:
                #pass
            #await ctx.send(embed=embed)
            await self.player.play(track)
            self.playing = track
            while self.player.is_playing:
                await asyncio.sleep(1)
            if self.loopStatus < 2: self.index += 1
            if self.index >= len(self.queue):
                if self.loopStatus == 1:
                    self.index = 0
                    continue
                else: break

    #prints currently playing song
    async def nowPlaying(self, ctx):
        try:
            embed = discord.Embed(title="Now Playing", url=self.playing.uri, description=self.playing)
            try:
                embed.set_thumbnail(url=self.playing.thumb)
            except:
                pass
        except:
            embed = discord.Embed(title="Now Playing", description=self.playing)
        await ctx.send(embed=embed)

    #skips current song
    async def skip(self):
        await self.player.stop()

    #delete queue
    async def clearQueue(self):
        self.queue.clear()
        self.index = 0

    #pauses player
    async def pause(self):
        await self.player.set_pause(True)

    #resumes player
    async def resume(self):
        await self.player.set_pause(False)
        
    #shuffles queue
    async def shuffleQueue(self):
        pyShuffle(self.queue)

    #removes song
    async def remove(self, ctx, index):
        track = self.queue[index]
        embed = discord.Embed(title="Removed From Queue", url=track.uri, description=track)
        try:
            embed.set_thumbnail(url=track.thumb)
        except:
            pass
        await ctx.send(embed=embed)
        self.queue.pop(index)

    #toggles looping
    async def loop(self, ctx):
        if self.loopStatus <= 1: self.loopStatus += 1
        else: self.loopStatus = 0
        if self.loopStatus == 0: await ctx.send("`Looping disabled.`")
        elif self.loopStatus == 1: await ctx.send("`Looping queue.`")
        elif self.loopStatus == 2: await ctx.send("`Looping current track.`")

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

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

@bot.command(hidden=True, brief="Returns bot state")
async def info(ctx):
    print(f"cmdInfo: Permission given ({ctx.message.author}).")
    await ctx.send('Music logged in as {0} ({0.id})'.format(bot.user) + " from " + auth.env + ".")

@bot.command(brief="Connects bot to voice", description="Connects bot to whichever voice channel the user is in.", aliases=["hi", "join"])
async def connect(ctx):
    player = playerMap[ctx.guild.id]
    await player.connect(ctx)

@bot.command(brief="Disconnects bot from voice", description="Disconnects bot from voice.", aliases=["die", "leave"])
async def disconnect(ctx):
    player = playerMap[ctx.guild.id]
    await player.clearQueue()
    await player.disconnect()
    await ctx.send("`Disconnected.`")

@bot.command(brief="Plays specified song", description="Plays specified song.", aliases=["p"])
async def play(ctx, *args):
    query = ' '.join(args[:])
    query = query.strip('<>')
    player = playerMap[ctx.guild.id]
    if "http" in query and "spotify" in query and "playlist" in query:
        query = query.rsplit('/', 1)[-1]
        playlist = sp.playlist(query)
        for track in playlist['tracks']['items']:
            title = track['track']['name']
            artist = track['track']['artists'][0]['name']
            query = f'ytsearch:{title} {artist} audio'
            res = await bot.wavelink.get_tracks(query)
            player.queue.append(res[0])
    else:
        if "http" in query and "spotify" in query and "track" in query:
            track = sp.track(query)
            query = f'ytsearch:{track["name"]}'
        elif not urlReg.match(query): query = f'ytsearch:{query}'
        res = await bot.wavelink.get_tracks(query)
        if not res: await ctx.send('`Could not find any songs with that query.`')
        else:
            if isinstance(res, wavelink.TrackPlaylist):
                for track in res.tracks: player.queue.append(track)
                playlist = True
            else: 
                player.queue.append(res[0])
                playlist = False
    await player.connect(ctx)
    if not player.player.is_playing: await player.play(ctx)
    else:
        if playlist: await ctx.send(f"`Added {len(res.tracks)} songs to the queue.`")
        else:
            embed = discord.Embed(title="Added to Queue", url=res[0].uri, description=res[0])
            try: embed.set_thumbnail(url=res[0].thumb)
            except: pass
            await ctx.send(embed=embed)

@bot.command(brief="Displays the queue", description="Displays the queue.", aliases=["q"])
async def queue(ctx):
    player = playerMap[ctx.guild.id]
    await player.getQueue(ctx)

@bot.command(brief="Displays currently playing song", description="Displays currently playing song.", aliases=["playing", "np", "song"])
async def nowplaying(ctx):
    player = playerMap[ctx.guild.id]
    await player.nowPlaying(ctx)

@bot.command(brief="Skips currently playing song", description="Skips currently playing song.", aliases=["s"])
async def skip(ctx, *args):
    input = ' '.join(args[:])
    player = playerMap[ctx.guild.id]
    try:
        if len(player.queue) >= int(input): 
            player.index = int(input - 2)
            await player.skip()
            await ctx.send(f"`Skipped to track {input}.`")
        else:
            await player.skip()
            await ctx.send("`Track skipped.`")
    except:
        await player.skip()
        await ctx.send("`Track skipped.`")

@bot.command(brief="Shuffles queue", description="Shuffles queue.")
async def shuffle(ctx):
    player = playerMap[ctx.guild.id]
    await player.shuffleQueue()
    await ctx.send("`Queue shuffled.`")

@bot.command(brief="Clears queue", description="Clears queue.")
async def clear(ctx):
    player = playerMap[ctx.guild.id]
    await player.clearQueue()
    await ctx.send("`Queue cleared.`")

@bot.command(brief="Pauses player", description="Pauses player.")
async def pause(ctx):
    player = playerMap[ctx.guild.id]
    if player.player.is_paused:
        await ctx.send("`This player is already paused.`")
    else:
        await player.pause()
        await ctx.send("`Player paused.`")

@bot.command(brief="Resumes paused player", description="Resumes paused player.", aliases=["unpause"])
async def resume(ctx):
    player = playerMap[ctx.guild.id]
    if not player.player.is_paused:
        await ctx.send("`This player is already playing.`")
    else:
        await player.resume()
        await ctx.send("`Player resumed.`")
        
@bot.command(brief="Loops the queue", description="Loops the queue.", aliases=["l"])
async def loop(ctx):
    player = playerMap[ctx.guild.id]
    await player.loop(ctx)

@bot.command(brief="Removes specified song", description="Removes specified song.", aliases=["r"])
async def remove(ctx, index):
    player = playerMap[ctx.guild.id]
    index = int(index) - 1
    await player.remove(ctx, index)

bot.run(auth.TOKEN)