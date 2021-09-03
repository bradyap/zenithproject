import discord
from auth import auth
from discord.ext import commands
from discord.utils import get
import asyncio
import os
import json

#os path 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#utility functions
async def kickTimer(ctx, member:discord.Member, time):
        print("kickTimer called.")
        await ctx.send(f"Member {member.display_name} will be kicked after {time} hour(s).")
        time = time * 3600
        await asyncio.sleep(time)
        try:
            await member.kick()
            await ctx.send(f"Member {member.display_name} was kicked after timer expire.")
        except discord.Forbidden:
            await ctx.send("Member kick failed after timer expire.")

async def vcKicker(ctx, member:discord.Member):
    while True:
        if member.voice == None:
            await member.kick()
            break
        else:
            await asyncio.sleep(60)
    await ctx.send(f"Member {member.display_name} was kicked after leaving vc.")

class Admin(commands.Cog, description="Server administration"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Kicks specified user", description="Kicks  specified user. Command useable by those with kick members permission.")
    async def kick(self, ctx, member:discord.Member):
        if ctx.message.author.guild_permissions.kick_members:
            try:
                await member.kick()
            except discord.Forbidden:
                await ctx.send(":(")
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.command(brief="Changes mentioned user's nickname", description="Changes mentioned user's nickname.")
    async def nick(self, ctx, user, *args):
        if ctx.message.author.guild_permissions.manage_nicknames:
            name = " ".join(args[:])
            target = ctx.message.mentions[0]
            try:
                await target.edit(nick=name)
                await ctx.send(f"Nickname for {target} changed to {name}.")
            except:
                await ctx.send(f"Nickname change for {target} unsuccessful. Please confirm that entered nickname is below the 32 character limit.")
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.command(brief="Mutes mentioned user in text channels", description="Mutes mentioned user in text channels.")
    async def mute(self, ctx):
        if ctx.message.author.guild_permissions.mute_members:
            guild = ctx.guild
            try:
                member = ctx.message.mentions[0]
                if get(ctx.guild.roles, name="Muted"):
                    role = discord.utils.get(ctx.message.guild.roles, name = "Muted")
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
                await member.add_roles(role)
            except discord.Forbidden:
                await ctx.send("Check bot permissions.")
            except:
                await ctx.send("Please mention a user.")
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.command(brief="Unmutes previously muted user", description="Unmutes previously muted user.")
    async def unmute(self, ctx):
        if ctx.message.author.guild_permissions.mute_members:
            guild = ctx.guild
            try:
                member = ctx.message.mentions[0]
                if get(ctx.guild.roles, name="Muted"):
                    role = discord.utils.get(ctx.message.guild.roles, name = "Muted")
                    if role in member.roles:
                        await member.remove_roles(role)
                    else:
                        await ctx.send("Mentioned user is not muted.")
                else:
                    await ctx.send("Server does not have mute role.")
            except discord.Forbidden:
                await ctx.send("Check bot permissions.")
            except:
                await ctx.send("Please mention a user.")
        else:
            await ctx.send("You do not have permission to use this command.")
            
    @commands.command(brief="Delete a chosen number of messages", description="Delete a chosen number of messages. Command usable by those with manage messages permission.")
    async def purge(self, ctx, num):
        clear = int(num) + 1
        if ctx.message.author.guild_permissions.manage_messages:
            await ctx.channel.purge(limit=clear)
        else: 
            await ctx.send("You do not have permission to use this command.")

    @commands.command(brief="Creates an invite to this server", description="Creates an invite to this server.")
    async def invite(self, ctx):
        link = await ctx.channel.create_invite(max_age = 0)
        await ctx.send(link)

    @commands.command(brief="Kicks mentioned user after a specified amount of time", description="Kicks mentioned user after a specific amount of time (hours).")
    async def timekick(self, ctx, member:discord.Member, time, unit):
        if ctx.message.author.guild_permissions.kick_members:
            if str(unit) == "minute" or str(unit) == "minutes" or str(unit) == "min" or str(unit) == "mins":
                time = round(float(time) / 60, 2)
            await kickTimer(ctx, member, time)
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.command(brief="Kicks mentioned user after they leave vc", description="Kicks mentioned user after they leave vc.")
    async def vckick(self, ctx, member:discord.Member):
        if ctx.message.author.guild_permissions.kick_members:
            if member.voice == None:
                await ctx.send(f"Member {member.display_name} is not in a vc.")
            else:
                await ctx.send(f"Member {member.display_name} will be kicked after they leave vc.")
                await vcKicker(ctx, member)
                    
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.command(brief='Enables or disables server-specific "level 2" features', description='Enables or disables server-specific "level 2" features.')
    async def level2(self, ctx, *args):
        if ctx.message.author.id == auth.brady:
            filename = "/home/brady_p/zenithproject/zenithlegacy/level2/" + str(ctx.guild.id) + ".json"
            if args[0] == "enable":
                if not os.path.exists(filename):
                    await ctx.send("Level 2 features enabled for this server.")
                    data = {}
                    #tts config
                    data["tts"] = {}
                    data["tts"]["status"] = False
                    data["tts"]["lang"] = "en"
                    data["tts"]["tld"] = "com"
                    #roles module config
                    data["roles"] = {}
                    data["roles"]["status"] = False
                    data["roles"]["rolelist"] = {}
                    #confessions config
                    data["confessions"] = {}
                    data["confessions"]["status"] = False
                    data["confessions"]["channel"] = 0
                    data["confessions"]["logs"] = {}
                    data["confessions"]["cooldowns"] = {}
                    data["confessions"]["muted"] = {}
                    data["confessions"]["banned"] = []
                    with open (filename, 'w') as f:
                        json.dump(data, f, indent=4)
                else: await ctx.send("Level 2 is already enabled on this server.")
            elif args[0] == "disable":
                await ctx.send("This will remove configuration files for all previously used level 2 features. Are you sure? (y/n)")
                def check(m):
                    return m.author == ctx.author
                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=5)
                    if msg.content == "y" or msg.content == "Y":
                        if os.path.exists(filename):
                            os.remove(filename)
                            await ctx.send("Level 2 features disabled for this server.")
                        else:
                            await ctx.send("Level 2 features are not enabled on this server.")
                    else:
                        await ctx.send("Canceled.")
                except asyncio.TimeoutError:
                    await ctx.send("Canceled (timeout).")
            elif args[0] == "tts":
                if args[1] == "enable":
                    if os.path.exists(filename):
                        with open (filename) as f:
                            data = json.load(f)
                        tts = data["tts"]
                        tts["status"] = True
                        await ctx.send("Tts enabled.")
                        with open (filename, 'w') as f:
                            json.dump(data, f, indent=4)
                    else: await ctx.send("Level 2 features are not enabled on this server.")
                if args[1] == "disable":
                    if os.path.exists(filename):
                        with open (filename) as f:
                            data = json.load(f)
                        tts = data["tts"]
                        tts["status"] = False
                        await ctx.send("Tts disabled.")
                        with open (filename, 'w') as f:
                            json.dump(data, f, indent=4)
                    else: await ctx.send("Level 2 features are not enabled on this server.")
                elif args[1] == "addchannel":
                    if ctx.message.author.guild_permissions.administrator:
                        filename = "/home/brady_p/zenithproject/zenithlegacy/level2/" + str(ctx.guild.id) + ".json"
                        if os.path.exists(filename):
                            with open (filename) as f:
                                data = json.load(f)
                            tts = data["tts"]
                            tts["channels"].append(ctx.channel.id)
                            await ctx.send("Tts channel added.")
                            with open (filename, 'w') as f:
                                json.dump(data, f, indent=4)
                        else:
                            await ctx.send("Level 2 features are not enabled on this server.")
                    else: await ctx.send("You do not have permission to use this command.")
                elif args[1] == "removechannel":
                    if ctx.message.author.guild_permissions.administrator:
                        filename = "/home/brady_p/zenithproject/zenithlegacy/level2/" + str(ctx.guild.id) + ".json"
                        if os.path.exists(filename):
                            with open (filename) as f:
                                data = json.load(f)
                            tts = data["tts"]
                            if ctx.channel.id in tts["channels"]: 
                                tts["channels"].remove(ctx.channel.id)
                                await ctx.send("Tts channel removed.")
                                with open (filename, 'w') as f:
                                    json.dump(data, f, indent=4)
                            else:
                                await ctx.send("This channel is not tts enabled.")
                        else:
                            await ctx.send("Level 2 features are not enabled on this server.")
                    else: await ctx.send("You do not have permission to use this command.")
            elif args[0] == "roles":
                if args[1] == "enable":
                    if os.path.exists(filename):
                        with open (filename) as f:
                            data = json.load(f)
                        roles = data["roles"]
                        roles["status"] = True
                        await ctx.send("Roles module enabled.")
                        with open (filename, 'w') as f:
                            json.dump(data, f, indent=4)
                    else: await ctx.send("Level 2 features are not enabled on this server.")
                if args[1] == "disable":
                    if os.path.exists(filename):
                        with open (filename) as f:
                            data = json.load(f)
                        roles = data["roles"]
                        roles["status"] = False
                        await ctx.send("Roles module disabled.")
                        with open (filename, 'w') as f:
                            json.dump(data, f, indent=4)
                    else: await ctx.send("Level 2 features are not enabled on this server.")
            elif args[0] == "confessions":
                if args[1] == "enable":
                    if os.path.exists(filename):
                        with open (filename) as f:
                            data = json.load(f)
                        confessions = data["confessions"]
                        confessions["status"] = True
                        await ctx.send("Confessions enabled. Please make sure you specify a channel.")
                        with open (filename, 'w') as f:
                            json.dump(data, f, indent=4)
                    else: await ctx.send("Level 2 features are not enabled on this server.")
                if args[1] == "disable":
                    if os.path.exists(filename):
                        with open (filename) as f:
                            data = json.load(f)
                        confessions = data["confessions"]
                        confessions["status"] = False
                        await ctx.send("Confessions disabled.")
                        with open (filename, 'w') as f:
                            json.dump(data, f, indent=4)
                    else: await ctx.send("Level 2 features are not enabled on this server.")
            else: 
                await ctx.send("Invalid argument.")
        else:
            await ctx.send("You do not have permission to use this command.")

def setup(bot):
    bot.add_cog(Admin(bot))