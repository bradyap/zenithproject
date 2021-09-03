import discord
from auth import auth
from discord.ext import commands
import asyncio
from random import shuffle as pyShuffle
import os
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import wavelink
from gtts import gTTS
import eyed3
import json

#os path 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#url regex
urlReg = re.compile(r'https?://(?:www\.)?.+')

#spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=auth.spotifyId, client_secret=auth.spotifySecret))

#player map
global playerMap
playerMap = {}

#tts
global tts_count
tts_count = 0

class Player:
    def __init__(self, bot, guild):
        self.gId = guild.id
        self.player = bot.wavelink.get_player(self.gId)
        #self.queue = asyncio.Queue()
        self.queue = []
        self.index = 0
        self.loopStatus = 0
        self.playing = "No song is currently playing."

    #connect
    async def connect(self, author, channel):
        if not self.player.is_connected:
            try:
                vc = author.voice.channel
                await channel.send(f"`Connecting to {vc.name}.`")
                await self.player.connect(vc.id)
            except AttributeError:
                await channel.send("`Please join a voice channel.`")

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
    async def play(self):
        while True:
            track = self.queue[self.index]
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

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wavelink.initiate_node(host=auth.lavaIp, port=auth.lavaPort, rest_uri=auth.lavaAddr, password=auth.lavaPw, identifier='MAIN', region='us_east')
        for guild in self.bot.guilds:
            playerMap[guild.id] = Player(self.bot, guild)

class Music(commands.Cog, description="Music bot functionality"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Connects bot to voice", description="Connects bot to whichever voice channel the user is in.", aliases=["hi", "join"])
    async def connect(self, ctx):
        player = playerMap[ctx.guild.id]
        await player.connect(ctx.author, ctx.channel)

    @commands.command(brief="Disconnects bot from voice", description="Disconnects bot from voice.", aliases=["die", "leave"])
    async def disconnect(self, ctx):
        player = playerMap[ctx.guild.id]
        await player.clearQueue()
        await player.disconnect()
        os.system("rm -rf /home/brady_p/zenithproject/zenithlegacy/tts/*")
        await ctx.send("`Disconnected.`")

    @commands.command(brief="Plays specified song", description="Plays specified song.", aliases=["p"])
    async def play(self, ctx, *args):
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
                res = await self.bot.wavelink.get_tracks(query)
                player.queue.append(res[0])
        else:
            if "http" in query and "spotify" in query and "track" in query:
                track = sp.track(query)
                query = f'ytsearch:{track["name"]}'
            elif not urlReg.match(query): query = f'ytsearch:{query}'
            res = await self.bot.wavelink.get_tracks(query)
            if not res: await ctx.send('`Could not find any songs with that query.`')
            else:
                if isinstance(res, wavelink.TrackPlaylist):
                    for track in res.tracks: player.queue.append(track)
                    playlist = True
                else: 
                    player.queue.append(res[0])
                    playlist = False
        await player.connect(ctx.author, ctx.channel)
        if not player.player.is_playing: await player.play()
        else:
            if playlist: await ctx.send(f"`Added {len(res.tracks)} songs to the queue.`")
            else:
                embed = discord.Embed(title="Added to Queue", url=res[0].uri, description=res[0])
                try: embed.set_thumbnail(url=res[0].thumb)
                except: pass
                await ctx.send(embed=embed)

    @commands.command(brief="Converts specified text to speech", description="Converts specified text to speech.")
    async def tts(self, ctx, *input):
        jsonname = "/home/brady_p/zenithproject/zenithlegacy/level2/" + str(ctx.guild.id) + ".json"
        if os.path.exists(jsonname):
            with open (jsonname) as f:
                data = json.load(f)
            tts = data["tts"]
            if tts["status"]:
                global tts_count
                query = ' '.join(input[:])
                player = playerMap[ctx.guild.id]
                file = gTTS(query, lang=tts["lang"], tld=tts["tld"])
                filename = "/home/brady_p/zenithproject/zenithlegacy/tts/" + str(tts_count) + ".mp3"
                tts_count += 1
                file.save(filename)
                audiofile = eyed3.load(filename)
                if (audiofile.tag == None): audiofile.initTag()
                audiofile.tag.title = input[0] + ".."
                audiofile.tag.save(filename)
                res = await self.bot.wavelink.get_tracks(filename)
                player.queue.append(res[0])
                await player.connect(ctx.author, ctx.channel)
                if not player.player.is_playing: await player.play()
                else:
                    await ctx.send("`Added TTS to queue.`")
            else: await ctx.send("Tts is not enabled on this server")
        else: await ctx.send("Level 2 features are not enabled on this server.")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            jsonname = "/home/brady_p/zenithproject/zenithlegacy/level2/" + message.guild.name.replace(" ", "_") + ":" + str(message.guild.id) + ".json"
            if os.path.exists(jsonname):
                with open (jsonname) as f:
                    data = json.load(f)
                tts = data["tts"]
                if tts["status"]:
                    if message.channel.id in tts["channels"]:
                        global tts_count
                        query = message.content
                        player = playerMap[message.guild.id]
                        file = gTTS(query, lang=tts["lang"], tld=tts["tld"])
                        filename = "/home/brady_p/zenithproject/zenithlegacy/tts/" + str(tts_count) + ".mp3"
                        tts_count += 1
                        file.save(filename)
                        audiofile = eyed3.load(filename)
                        if (audiofile.tag == None): audiofile.initTag()
                        audiofile.tag.title = query.split()[0] + ".."
                        audiofile.tag.save(filename)
                        res = await self.bot.wavelink.get_tracks(filename)
                        player.queue.append(res[0])
                        await player.connect(message.author, message.channel)
                        if not player.player.is_playing: await player.play()
                        else:
                            await message.channel.send("`Added TTS to queue.`")
        
    @commands.command(brief="Configuration options for tts", description="Configuration options for tts.")
    async def ttsconfig(self, ctx, *args):
        if args[0] == "lang":
            jsonname = "/home/brady_p/zenithproject/zenithlegacy/level2/" + str(ctx.guild.id) + ".json"
            if os.path.exists(jsonname):
                with open (jsonname) as f:
                    data = json.load(f)
                tts = data["tts"]
                if tts["status"]:
                    tts["lang"] = args[1]
                    await ctx.send("Tts language updated.")
                    with open (jsonname, 'w') as f:
                        json.dump(data, f, indent=4)
                else: await ctx.send("Tts is not enabled on this server")
            else: await ctx.send("Level 2 features are not enabled on this server.")
        elif args[0] == "tld":
            jsonname = "/home/brady_p/zenithproject/zenithlegacy/level2/" + str(ctx.guild.id) + ".json"
            if os.path.exists(jsonname):
                with open (jsonname) as f:
                    data = json.load(f)
                tts = data["tts"]
                if tts["status"]:
                    tts["tld"] = args[1]
                    await ctx.send("Tts tld updated.")
                    with open (jsonname, 'w') as f:
                        json.dump(data, f, indent=4)
                else: await ctx.send("Tts is not enabled on this server")
            else: await ctx.send("Level 2 features are not enabled on this server.")
        elif args[0] == "help":
            await ctx.send(file=discord.File("../content/tts_help.png"))
        else: 
            await ctx.send("Invalid argument.")
    
    @commands.command(brief="Displays the queue", description="Displays the queue.", aliases=["q"])
    async def queue(self, ctx):
        player = playerMap[ctx.guild.id]
        await player.getQueue(ctx)

    @commands.command(brief="Displays currently playing song", description="Displays currently playing song.", aliases=["playing", "np", "song"])
    async def nowplaying(self, ctx):
        player = playerMap[ctx.guild.id]
        await player.nowPlaying(self, ctx)

    @commands.command(brief="Skips currently playing song", description="Skips currently playing song.", aliases=["s"])
    async def skip(self, ctx, *args):
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

    @commands.command(brief="Shuffles queue", description="Shuffles queue.")
    async def shuffle(self, ctx):
        player = playerMap[ctx.guild.id]
        await player.shuffleQueue()
        await ctx.send("`Queue shuffled.`")

    @commands.command(brief="Clears queue", description="Clears queue.")
    async def clear(self, ctx):
        player = playerMap[ctx.guild.id]
        await player.clearQueue()
        await ctx.send("`Queue cleared.`")

    @commands.command(brief="Pauses player", description="Pauses player.")
    async def pause(self, ctx):
        player = playerMap[ctx.guild.id]
        if player.player.is_paused:
            await ctx.send("`This player is already paused.`")
        else:
            await player.pause()
            await ctx.send("`Player paused.`")

    @commands.command(brief="Resumes paused player", description="Resumes paused player.", aliases=["unpause"])
    async def resume(self, ctx):
        player = playerMap[ctx.guild.id]
        if not player.player.is_paused:
            await ctx.send("`This player is already playing.`")
        else:
            await player.resume()
            await ctx.send("`Player resumed.`")
            
    @commands.command(brief="Loops the queue", description="Loops the queue.", aliases=["l"])
    async def loop(self, ctx):
        player = playerMap[ctx.guild.id]
        await player.loop(ctx)

    @commands.command(brief="Removes specified song", description="Removes specified song.", aliases=["r"])
    async def remove(self, ctx, index):
        player = playerMap[ctx.guild.id]
        index = int(index) - 1
        await player.remove(self, ctx, index)

def setup(bot):
    bot.add_cog(Events(bot))
    bot.add_cog(Music(bot))